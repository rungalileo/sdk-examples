"""
Weather Vibes Agent implementation using the Simple Agent Framework.
"""

import os
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader

from agent_framework.agent import Agent
from agent_framework.state import AgentState
from agent_framework.models import ToolMetadata
from openai import OpenAI

# Configure proper path for imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# import tools
from tools.weather_tool import WeatherTool
from tools.recommendation_tool import RecommendationsTool
from tools.youtube_tool import YouTubeTool
from agent.descriptor import WEATHER_VIBES_DESCRIPTOR

# Configure standard logging
logger = logging.getLogger("weather_vibes_agent")


# Add metadata class methods to tools to match the updated API
def create_tool_metadata(name, description, tags=None):
    @classmethod
    def metadata(cls):
        return ToolMetadata(
            name=name,
            description=description,
            tags=tags or [],
            input_schema={"type": "object", "properties": {}, "required": []},
            output_schema={"type": "object", "properties": {}, "required": []},
        )

    return metadata


# Add metadata method to the tool classes if they don't have it
if not hasattr(WeatherTool, "metadata"):
    WeatherTool.metadata = create_tool_metadata(
        "get_weather",
        "Get the current weather conditions for a location",
        ["weather", "utility"],
    )

if not hasattr(RecommendationsTool, "metadata"):
    RecommendationsTool.metadata = create_tool_metadata(
        "get_recommendations",
        "Get recommendations for items to bring based on weather conditions",
        ["weather", "recommendations"],
    )

if not hasattr(YouTubeTool, "metadata"):
    YouTubeTool.metadata = create_tool_metadata(
        "find_weather_video",
        "Find a YouTube video that matches the weather vibe",
        ["youtube", "entertainment"],
    )


class WeatherVibesAgent(Agent):
    """
    Agent that provides weather information, recommendations, and matching videos.
    Implements the Agent Connect Protocol (ACP) for standardized communication.
    """

    def __init__(self, agent_id: str = "weather_vibes"):
        super().__init__(agent_id=agent_id)

        # Initialize state - the API has changed, so we use direct assignment now
        # Changed from self.state.set() to direct attribute assignment
        self.state = AgentState()

        # Default state initialization using direct attributes
        # Instead of self.state.set("search_history", []), use:
        if not hasattr(self.state, "search_history"):
            self.state.search_history = []
        if not hasattr(self.state, "favorite_locations"):
            self.state.favorite_locations = []

        # Set up template environment
        template_dir = Path(__file__).parent.parent / "templates"
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True
        )

        # Set up OpenAI client instead of OpenAIChat
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Instead of AgentLogger, use standard Python logging
        self.agent_id = agent_id
        logger.info(f"Initialized WeatherVibesAgent with ID: {self.agent_id}")

        # Initialize tool instances directly
        self.weather_tool = None
        self.recommendations_tool = None
        self.youtube_tool = None

        # Register tools
        self._register_tools()

        # Store descriptor
        self.descriptor = WEATHER_VIBES_DESCRIPTOR

    def _register_tools(self) -> None:
        """Register agent-specific tools"""
        # First, inspect what type of object tool_registry is
        logger.info(f"Tool registry type: {type(self.tool_registry)}")

        try:
            # Create tool instances and store them directly
            self.weather_tool = WeatherTool()
            self.recommendations_tool = RecommendationsTool()
            self.youtube_tool = YouTubeTool()

            # Register tools with metadata and implementation
            self.tool_registry.register(
                metadata=WeatherTool.metadata(), implementation=self.weather_tool
            )

            self.tool_registry.register(
                metadata=RecommendationsTool.metadata(),
                implementation=self.recommendations_tool,
            )

            self.tool_registry.register(
                metadata=YouTubeTool.metadata(), implementation=self.youtube_tool
            )

            logger.info("Tools registered successfully")

        except Exception as e:
            logger.error(f"Failed to register tools: {e}")
            raise

    async def _generate_system_prompt(self) -> str:
        """Generate the system prompt using the template"""
        template = self.template_env.get_template("system.j2")
        return template.render(
            search_history=getattr(self.state, "search_history", []),
            favorite_locations=getattr(self.state, "favorite_locations", []),
        )

    async def _format_result(self, result: Any) -> Dict[str, Any]:
        """
        Format the result from processing.

        This is an abstract method required by the Agent base class.
        It formats the raw result into a standard structure.

        Args:
            result: The raw result from processing

        Returns:
            A formatted result dictionary
        """
        if isinstance(result, dict):
            return result
        elif hasattr(result, "model_dump"):
            # Handle pydantic models
            return result.model_dump()
        elif hasattr(result, "__dict__"):
            # Handle objects with __dict__
            return result.__dict__
        else:
            # Default case
            return {"result": str(result)}

    async def get_acp_descriptor(self) -> Dict[str, Any]:
        """
        Return the ACP descriptor for this agent.
        This implements the ACP agent discovery capability.
        """
        return self.descriptor

    async def process_acp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an ACP request and generate a response.
        This implements the ACP run execution capability.

        Args:
            request: The ACP request payload

        Returns:
            An ACP response payload
        """
        # Replace AgentLogger methods with standard logging
        logger.info(f"Processing ACP request: {json.dumps(request)[:100]}...")

        try:
            # Extract relevant information from the request
            input_data = request.get("input", {})
            config = request.get("config", {})
            metadata = request.get("metadata", {})

            # Parse input and config
            location = input_data.get("location")
            units = input_data.get("units", "metric")
            verbose = config.get("verbose", False)
            max_recommendations = config.get("max_recommendations", 5)
            video_mood = config.get("video_mood")

            # Validate input
            if not location:
                logger.error("Invalid input: 'location' field is required")
                return {
                    "error": 400,
                    "message": "Invalid input: 'location' field is required",
                }

            # Update search history
            if not hasattr(self.state, "search_history"):
                self.state.search_history = []

            if location not in self.state.search_history:
                self.state.search_history.append(location)
                # Keep only last 5 items
                if len(self.state.search_history) > 5:
                    self.state.search_history = self.state.search_history[-5:]

            # Step 1: Get weather information
            logger.info(f"Getting weather for location: {location}")

            weather_result = await self.weather_tool.execute(location=location, days=1)
            if "error" in weather_result:
                logger.error(f"Weather API error: {weather_result['message']}")
                return {
                    "error": 500,
                    "message": f"Weather API error: {weather_result['message']}",
                }

            # Step 2: Get recommendations
            logger.info(f"Getting recommendations based on weather")
            recommendations = await self.recommendations_tool.execute(
                weather=weather_result, max_items=max_recommendations
            )

            # Step 3: Get matching YouTube video
            logger.info(
                f"Finding YouTube video matching weather condition: {weather_result['condition']}"
            )
            video_result = await self.youtube_tool.execute(
                weather_condition=weather_result["condition"], mood_override=video_mood
            )

            # Prepare the response
            result = {
                "weather": weather_result,
                "recommendations": recommendations,
                "video": video_result,
            }

            # If not verbose, filter out some weather details
            if not verbose and "weather" in result:
                result["weather"] = {
                    "location": weather_result["location"],
                    "temperature_c": weather_result["temperature_c"],
                    "condition": weather_result["condition"],
                    "humidity": weather_result["humidity"],
                    "wind_kph": weather_result["wind_kph"],
                }

            # Format response according to ACP standards
            response = {"output": result}

            # Add the original agent_id to the response
            if "agent_id" in request:
                response["agent_id"] = request["agent_id"]

            # Add metadata if present in the request
            if metadata:
                response["metadata"] = metadata

            logger.info(f"Successfully processed request for location: {location}")
            return response

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {"error": 500, "message": f"Error processing request: {str(e)}"}
