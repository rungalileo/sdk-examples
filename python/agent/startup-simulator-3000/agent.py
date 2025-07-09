#!/usr/bin/env python3
"""
Simple Agent for Startup Pitch Generation
This agent generates startup pitches using different tools based on the selected mode.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from galileo import GalileoLogger
from galileo.openai import openai

from agent_framework.agent import Agent
from agent_framework.models import VerbosityLevel, ToolSelectionHooks
from agent_framework.llm.openai_provider import OpenAIProvider
from agent_framework.llm.models import LLMConfig
from agent_framework.utils.logging import ConsoleAgentLogger
from agent_framework.utils.tool_hooks import LoggingToolHooks, LoggingToolSelectionHooks

# Import all available tools
from tools.startup_simulator import StartupSimulatorTool
from tools.serious_startup_simulator import SeriousStartupSimulatorTool
from tools.hackernews_tool import HackerNewsTool
from tools.news_api_tool import NewsAPITool
from tools.text_analysis import TextAnalyzerTool
from tools.keyword_extraction import KeywordExtractorTool

# Load environment variables
load_dotenv()

# Use the Galileo-wrapped OpenAI client
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class SimpleAgent(Agent):
    """
    A simple agent that generates startup pitches.

    This agent demonstrates:
    1. Tool-based architecture with specialized tools
    2. Mode-based execution (silly vs serious)
    3. Galileo observability with proper span logging
    4. Context-aware tool execution
    """

    def __init__(
        self,
        verbosity: VerbosityLevel = VerbosityLevel.LOW,
        logger: Optional[ConsoleAgentLogger] = None,
        tool_selection_hooks: Optional[ToolSelectionHooks] = None,
        metadata: Optional[Dict[str, Any]] = None,
        llm_provider: Optional[OpenAIProvider] = None,
        mode: str = "silly",
    ):
        # Create default LLM config if not provided
        if llm_provider is None:
            llm_config = LLMConfig(model="gpt-4", temperature=0.7, max_tokens=1000)
            llm_provider = OpenAIProvider(config=llm_config)

        # Initialize the base Agent class with configuration
        super().__init__(
            agent_id=f"startup-agent-{mode}",
            verbosity=verbosity,
            logger=logger or ConsoleAgentLogger(f"startup-agent-{mode}"),
            tool_selection_hooks=tool_selection_hooks
            or LoggingToolSelectionHooks(
                logger or ConsoleAgentLogger(f"startup-agent-{mode}")
            ),
            metadata=metadata or {},
            llm_provider=llm_provider,
        )

        self.mode = mode
        self.task_parameters = {}

        # Register all available tools
        self._register_tools()

        # Set up logger with tool hooks
        if self.logger:
            self._setup_logger(self.logger)

    def _register_tools(self) -> None:
        """
        Register all available tools with the agent's tool registry.

        Think of tools as specialized functions that the agent can call.
        Each tool has:
        - A name and description
        - Input/output schemas (what it expects and returns)
        - Tags for categorization
        - An implementation (the actual code that runs)

        The agent will automatically choose which tools to use based on the task.
        """

        # Text analysis tool - can analyze and process text content
        self.tool_registry.register(
            metadata=TextAnalyzerTool.get_metadata(), implementation=TextAnalyzerTool
        )

        # Keyword extraction tool - finds important words/phrases in text
        self.tool_registry.register(
            metadata=KeywordExtractorTool.get_metadata(),
            implementation=KeywordExtractorTool,
        )

        # Startup simulator tool - generates silly, creative startup pitches
        # Used in "silly" mode
        self.tool_registry.register(
            metadata=StartupSimulatorTool.get_metadata(),
            implementation=StartupSimulatorTool,
        )

        # Serious startup simulator tool - generates professional business plans
        # Used in "serious" mode
        self.tool_registry.register(
            metadata=SeriousStartupSimulatorTool.get_metadata(),
            implementation=SeriousStartupSimulatorTool,
        )

        # HackerNews tool - fetches trending tech stories for inspiration
        # Used in "silly" mode to get creative context
        self.tool_registry.register(
            metadata=HackerNewsTool.get_metadata(), implementation=HackerNewsTool
        )

        # NewsAPI tool - fetches business news for market analysis
        # Used in "serious" mode to get professional context
        self.tool_registry.register(
            metadata=NewsAPITool.get_metadata(), implementation=NewsAPITool
        )

    async def _format_result(
        self, task: str, results: List[tuple[str, Any]], galileo_logger: GalileoLogger
    ) -> str:
        """
        Format the final result from tool executions.

        This method takes the raw outputs from all the tools and formats them
        into a coherent, user-friendly response. It's like the final step in
        a recipe where you plate the dish nicely.

        Args:
            task: The original user request
            results: List of (tool_name, result) tuples from executed tools
            galileo_logger: Galileo logger instance for span creation

        Returns:
            Formatted string response for the user
        """

        # Add LLM span for result formatting
        galileo_logger.add_llm_span(
            input=f"Formatting results for task: {task}",
            output="Formatting started",
            model="result_formatter",
            num_input_tokens=len(str(results)),
            num_output_tokens=0,
            total_tokens=len(str(results)),
            duration_ns=0,
        )

        try:
            # Check for silly mode first - look for startup_simulator tool results
            for tool_name, result in results:
                if tool_name == "startup_simulator":
                    # Parse the JSON string result from Galileo-formatted output
                    try:
                        if isinstance(result, str):
                            parsed_result = json.loads(result)
                            pitch = parsed_result.get("pitch", "")
                        else:
                            # Fallback for dict format
                            pitch = result.get("pitch", "")

                        # Log full structured result to Galileo for observability
                        result_data = {
                            "tool": tool_name,
                            "mode": "silly",
                            "full_result": result,
                            "extracted_pitch": pitch,
                        }
                        print(
                            f"Agent Result Data (Silly): {json.dumps(result_data, indent=2)}"
                        )

                        # Add LLM span for formatting completion
                        galileo_logger.add_llm_span(
                            input=f"Result formatting completed for {tool_name}",
                            output=pitch,
                            model="result_formatter",
                            num_input_tokens=len(str(result)),
                            num_output_tokens=len(pitch),
                            total_tokens=len(str(result)) + len(pitch),
                            duration_ns=0,
                        )

                        return pitch

                    except json.JSONDecodeError as e:
                        print(f"Error parsing startup simulator result: {e}")
                        galileo_logger.add_llm_span(
                            input=f"Error parsing result for {tool_name}",
                            output=str(e),
                            model="result_formatter",
                            num_input_tokens=len(str(result)),
                            num_output_tokens=len(str(e)),
                            total_tokens=len(str(result)) + len(str(e)),
                            duration_ns=0,
                        )
                        return str(result)

                elif tool_name == "serious_startup_simulator":
                    # Parse the JSON string result from Galileo-formatted output
                    try:
                        if isinstance(result, str):
                            parsed_result = json.loads(result)
                            pitch = parsed_result.get("pitch", "")
                        else:
                            # Fallback for dict format
                            pitch = result.get("pitch", "")

                        # Log full structured result to Galileo for observability
                        result_data = {
                            "tool": tool_name,
                            "mode": "serious",
                            "full_result": result,
                            "extracted_pitch": pitch,
                        }
                        print(
                            f"Agent Result Data (Serious): {json.dumps(result_data, indent=2)}"
                        )

                        # Add LLM span for formatting completion
                        galileo_logger.add_llm_span(
                            input=f"Result formatting completed for {tool_name}",
                            output=pitch,
                            model="result_formatter",
                            num_input_tokens=len(str(result)),
                            num_output_tokens=len(pitch),
                            total_tokens=len(str(result)) + len(pitch),
                            duration_ns=0,
                        )

                        return pitch

                    except json.JSONDecodeError as e:
                        print(f"Error parsing serious startup simulator result: {e}")
                        galileo_logger.add_llm_span(
                            input=f"Error parsing result for {tool_name}",
                            output=str(e),
                            model="result_formatter",
                            num_input_tokens=len(str(result)),
                            num_output_tokens=len(str(e)),
                            total_tokens=len(str(result)) + len(str(e)),
                            duration_ns=0,
                        )
                        return str(result)

            # If no startup simulator results found, return a summary
            summary = (
                f"Generated results for {len(results)} tools: {[r[0] for r in results]}"
            )
            galileo_logger.add_llm_span(
                input=f"No startup simulator results found",
                output=summary,
                model="result_formatter",
                num_input_tokens=len(str(results)),
                num_output_tokens=len(summary),
                total_tokens=len(str(results)) + len(summary),
                duration_ns=0,
            )
            return summary

        except Exception as e:
            galileo_logger.add_llm_span(
                input=f"Error in result formatting",
                output=str(e),
                model="result_formatter",
                num_input_tokens=len(str(results)),
                num_output_tokens=len(str(e)),
                total_tokens=len(str(results)) + len(str(e)),
                duration_ns=0,
            )
            raise e

    async def _execute_hackernews_tool(
        self, limit: int = 3, galileo_logger: GalileoLogger = None
    ) -> str:
        """
        Execute the HackerNews tool to get trending stories for context.

        This tool fetches recent HackerNews stories to provide creative inspiration
        for the startup pitch generation. It's used in "silly" mode.

        Args:
            limit: Number of stories to fetch
            galileo_logger: Galileo logger instance for span creation

        Returns:
            JSON string with HackerNews context
        """

        if galileo_logger:
            # Add LLM span for tool execution start
            galileo_logger.add_llm_span(
                input=f"Executing HackerNews tool with limit: {limit}",
                output="Tool execution started",
                model="hackernews_tool",
                num_input_tokens=len(str(limit)),
                num_output_tokens=0,
                total_tokens=len(str(limit)),
                duration_ns=0,
            )

        try:
            startup_tool_class = self.tool_registry.get_implementation(
                "hackernews_tool"
            )
            if startup_tool_class:
                startup_tool = startup_tool_class()
                startup_result = await startup_tool.execute(limit=limit)

                # Add LLM span for tool completion
                if galileo_logger:
                    galileo_logger.add_llm_span(
                        input=f"HackerNews tool execution completed",
                        output=(
                            startup_result[:200] + "..."
                            if len(startup_result) > 200
                            else startup_result
                        ),
                        model="hackernews_tool",
                        num_input_tokens=len(str(limit)),
                        num_output_tokens=len(startup_result),
                        total_tokens=len(str(limit)) + len(startup_result),
                        duration_ns=0,
                    )

                return startup_result

            # Tool not found
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"HackerNews tool not found",
                    output="",
                    model="hackernews_tool",
                    num_input_tokens=len(str(limit)),
                    num_output_tokens=0,
                    total_tokens=len(str(limit)),
                    duration_ns=0,
                )
            return ""

        except Exception as e:
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"Error in HackerNews tool execution",
                    output=str(e),
                    model="hackernews_tool",
                    num_input_tokens=len(str(limit)),
                    num_output_tokens=len(str(e)),
                    total_tokens=len(str(limit)) + len(str(e)),
                    duration_ns=0,
                )
            raise e

    async def _execute_news_api_tool(
        self,
        category: str = "business",
        limit: int = 5,
        galileo_logger: GalileoLogger = None,
    ) -> str:
        """
        Execute the NewsAPI tool to get business news for context.

        This tool fetches recent business news articles to provide market analysis
        and professional context for the startup plan generation. It's used in "serious" mode.

        Args:
            category: News category to fetch
            limit: Number of articles to fetch
            galileo_logger: Galileo logger instance for span creation

        Returns:
            JSON string with business news context
        """

        if galileo_logger:
            # Add LLM span for tool execution start
            galileo_logger.add_llm_span(
                input=f"Executing News API tool with category: {category}, limit: {limit}",
                output="Tool execution started",
                model="news_api_tool",
                num_input_tokens=len(str(category)) + len(str(limit)),
                num_output_tokens=0,
                total_tokens=len(str(category)) + len(str(limit)),
                duration_ns=0,
            )

        try:
            startup_tool_class = self.tool_registry.get_implementation("news_api_tool")
            if startup_tool_class:
                startup_tool = startup_tool_class()
                startup_result = await startup_tool.execute(
                    category=category, limit=limit
                )

                # Add LLM span for tool completion
                if galileo_logger:
                    galileo_logger.add_llm_span(
                        input=f"News API tool execution completed",
                        output=(
                            startup_result[:200] + "..."
                            if len(startup_result) > 200
                            else startup_result
                        ),
                        model="news_api_tool",
                        num_input_tokens=len(str(category)) + len(str(limit)),
                        num_output_tokens=len(startup_result),
                        total_tokens=len(str(category))
                        + len(str(limit))
                        + len(startup_result),
                        duration_ns=0,
                    )

                return startup_result

            # Tool not found
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"News API tool not found",
                    output="",
                    model="news_api_tool",
                    num_input_tokens=len(str(category)) + len(str(limit)),
                    num_output_tokens=0,
                    total_tokens=len(str(category)) + len(str(limit)),
                    duration_ns=0,
                )
            return ""

        except Exception as e:
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"Error in News API tool execution",
                    output=str(e),
                    model="news_api_tool",
                    num_input_tokens=len(str(category)) + len(str(limit)),
                    num_output_tokens=len(str(e)),
                    total_tokens=len(str(category)) + len(str(limit)) + len(str(e)),
                    duration_ns=0,
                )
            raise e

    async def _execute_startup_simulator(
        self,
        industry: str,
        audience: str,
        random_word: str,
        hn_context: str = "",
        galileo_logger: GalileoLogger = None,
    ) -> str:
        """
        Execute the startup simulator tool for silly mode.

        This tool generates creative, humorous startup pitches using HackerNews
        context for inspiration. It's the main tool used in "silly" mode.

        Args:
            industry: Target industry for the startup
            audience: Target audience for the startup
            random_word: Random word to include in the pitch
            hn_context: HackerNews context for inspiration
            galileo_logger: Galileo logger instance for span creation

        Returns:
            JSON string with generated startup pitch
        """

        if galileo_logger:
            # Add LLM span for tool execution start
            galileo_logger.add_llm_span(
                input=f"Executing startup simulator for {industry} targeting {audience} with word '{random_word}'",
                output="Tool execution started",
                model="startup_simulator",
                num_input_tokens=len(industry)
                + len(audience)
                + len(random_word)
                + len(hn_context),
                num_output_tokens=0,
                total_tokens=len(industry)
                + len(audience)
                + len(random_word)
                + len(hn_context),
                duration_ns=0,
            )

        try:
            startup_tool_class = self.tool_registry.get_implementation(
                "startup_simulator"
            )
            if startup_tool_class:
                startup_tool = startup_tool_class()
                startup_result = await startup_tool.execute(
                    industry=industry,
                    audience=audience,
                    random_word=random_word,
                    hn_context=hn_context,
                )

                # Add LLM span for tool completion
                if galileo_logger:
                    galileo_logger.add_llm_span(
                        input=f"Startup simulator execution completed",
                        output=(
                            startup_result[:200] + "..."
                            if len(startup_result) > 200
                            else startup_result
                        ),
                        model="startup_simulator",
                        num_input_tokens=len(industry)
                        + len(audience)
                        + len(random_word)
                        + len(hn_context),
                        num_output_tokens=len(startup_result),
                        total_tokens=len(industry)
                        + len(audience)
                        + len(random_word)
                        + len(hn_context)
                        + len(startup_result),
                        duration_ns=0,
                    )

                return startup_result

            # Tool not found
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"Startup simulator tool not found",
                    output="",
                    model="startup_simulator",
                    num_input_tokens=len(industry)
                    + len(audience)
                    + len(random_word)
                    + len(hn_context),
                    num_output_tokens=0,
                    total_tokens=len(industry)
                    + len(audience)
                    + len(random_word)
                    + len(hn_context),
                    duration_ns=0,
                )
            return ""

        except Exception as e:
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"Error in startup simulator execution",
                    output=str(e),
                    model="startup_simulator",
                    num_input_tokens=len(industry)
                    + len(audience)
                    + len(random_word)
                    + len(hn_context),
                    num_output_tokens=len(str(e)),
                    total_tokens=len(industry)
                    + len(audience)
                    + len(random_word)
                    + len(hn_context)
                    + len(str(e)),
                    duration_ns=0,
                )
            raise e

    async def _execute_serious_startup_simulator(
        self,
        industry: str,
        audience: str,
        random_word: str,
        news_context: str = "",
        galileo_logger: GalileoLogger = None,
    ) -> str:
        """
        Execute the serious startup simulator tool for professional mode.

        This tool generates professional, business-focused startup plans using
        business news context for market analysis. It's the main tool used in "serious" mode.

        Args:
            industry: Target industry for the startup
            audience: Target audience for the startup
            random_word: Random word to include in the plan
            news_context: Business news context for market analysis
            galileo_logger: Galileo logger instance for span creation

        Returns:
            JSON string with generated startup plan
        """

        if galileo_logger:
            # Add LLM span for tool execution start
            galileo_logger.add_llm_span(
                input=f"Executing serious startup simulator for {industry} targeting {audience} with word '{random_word}'",
                output="Tool execution started",
                model="serious_startup_simulator",
                num_input_tokens=len(industry)
                + len(audience)
                + len(random_word)
                + len(news_context),
                num_output_tokens=0,
                total_tokens=len(industry)
                + len(audience)
                + len(random_word)
                + len(news_context),
                duration_ns=0,
            )

        try:
            startup_tool_class = self.tool_registry.get_implementation(
                "serious_startup_simulator"
            )
            if startup_tool_class:
                startup_tool = startup_tool_class()
                startup_result = await startup_tool.execute(
                    industry=industry,
                    audience=audience,
                    random_word=random_word,
                    news_context=news_context,
                )

                # Add LLM span for tool completion
                if galileo_logger:
                    galileo_logger.add_llm_span(
                        input=f"Serious startup simulator execution completed",
                        output=(
                            startup_result[:200] + "..."
                            if len(startup_result) > 200
                            else startup_result
                        ),
                        model="serious_startup_simulator",
                        num_input_tokens=len(industry)
                        + len(audience)
                        + len(random_word)
                        + len(news_context),
                        num_output_tokens=len(startup_result),
                        total_tokens=len(industry)
                        + len(audience)
                        + len(random_word)
                        + len(news_context)
                        + len(startup_result),
                        duration_ns=0,
                    )

                return startup_result

            # Tool not found
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"Serious startup simulator tool not found",
                    output="",
                    model="serious_startup_simulator",
                    num_input_tokens=len(industry)
                    + len(audience)
                    + len(random_word)
                    + len(news_context),
                    num_output_tokens=0,
                    total_tokens=len(industry)
                    + len(audience)
                    + len(random_word)
                    + len(news_context),
                    duration_ns=0,
                )
            return ""

        except Exception as e:
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"Error in serious startup simulator execution",
                    output=str(e),
                    model="serious_startup_simulator",
                    num_input_tokens=len(industry)
                    + len(audience)
                    + len(random_word)
                    + len(news_context),
                    num_output_tokens=len(str(e)),
                    total_tokens=len(industry)
                    + len(audience)
                    + len(random_word)
                    + len(news_context)
                    + len(str(e)),
                    duration_ns=0,
                )
            raise e

    async def run(
        self, task: str, industry: str = "", audience: str = "", random_word: str = ""
    ) -> str:
        """
        Execute the agent's task with Galileo monitoring.

        This is the main entry point for the agent. It orchestrates the entire process:
        1. Stores user parameters for tool execution
        2. Starts Galileo tracing for observability
        3. Executes tools in sequence with proper context passing
        4. Formats the final result

        Args:
            task: The user's request (e.g., "generate a startup pitch")
            industry: Target industry for the startup
            audience: Target audience for the startup
            random_word: Random word to include in the pitch

        Returns:
            Formatted startup pitch as a string
        """

        # Store parameters for tool execution
        # These will be passed to individual tools as needed
        self.task_parameters = {
            "industry": industry,
            "audience": audience,
            "random_word": random_word,
        }

        # Log workflow start as JSON for observability
        # This helps us understand the agent's decision-making process
        workflow_data = {
            "agent_id": self.agent_id,
            "mode": self.mode,
            "task": task,
            "start_time": datetime.now().isoformat(),
            "tools_registered": list(self.tool_registry.get_all_tools().keys()),
        }
        print(f"Agent Workflow Start: {json.dumps(workflow_data, indent=2)}")

        # Get the centralized Galileo logger instance
        from agent_framework.utils.logging import get_galileo_logger

        galileo_logger = get_galileo_logger()

        # Start the main agent trace - this is the parent trace for the entire workflow
        trace = None
        if galileo_logger:
            trace = galileo_logger.start_trace(f"agent_workflow_{self.mode}")

        try:
            # Add LLM span for workflow start if logger is available
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"Agent workflow started for task: {task}",
                    output="Workflow initialization",
                    model="agent_workflow",
                    num_input_tokens=len(task),
                    num_output_tokens=0,
                    total_tokens=len(task),
                    duration_ns=0,
                )

            # Execute tools based on mode with proper context passing
            results = []

            if self.mode == "serious":
                # Step 1: Get news context first
                print("🔍 Step 1: Fetching business news for context...")
                news_context = await self._execute_news_api_tool(
                    category="business", limit=5, galileo_logger=galileo_logger
                )
                results.append(("news_api", news_context))

                # Step 2: Generate serious startup pitch using the news context
                print("📝 Step 2: Generating professional startup plan...")
                startup_result = await self._execute_serious_startup_simulator(
                    industry=industry,
                    audience=audience,
                    random_word=random_word,
                    news_context=news_context,
                    galileo_logger=galileo_logger,
                )
                results.append(("serious_startup_simulator", startup_result))

            else:  # silly mode
                # Step 1: Get HackerNews context first
                print("🔍 Step 1: Fetching HackerNews stories for inspiration...")
                hn_context = await self._execute_hackernews_tool(
                    limit=3, galileo_logger=galileo_logger
                )
                results.append(("hackernews", hn_context))

                # Step 2: Generate silly startup pitch using the HN context
                print("🎭 Step 2: Generating creative startup pitch...")
                startup_result = await self._execute_startup_simulator(
                    industry=industry,
                    audience=audience,
                    random_word=random_word,
                    hn_context=hn_context,
                    galileo_logger=galileo_logger,
                )
                results.append(("startup_simulator", startup_result))

            # Step 3: Format the final result
            print("✨ Step 3: Formatting final result...")
            formatted_result = await self._format_result(task, results, galileo_logger)

            # Log workflow completion as JSON
            completion_data = {
                "agent_id": self.agent_id,
                "mode": self.mode,
                "task": task,
                "end_time": datetime.now().isoformat(),
                "result_length": len(formatted_result),
                "tools_used": [result[0] for result in results],
                "execution_status": "success",
            }
            print(f"Agent Workflow Complete: {json.dumps(completion_data, indent=2)}")

            # Add LLM span for workflow completion if logger is available
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"Agent workflow completed successfully",
                    output=formatted_result,
                    model="agent_workflow",
                    num_input_tokens=len(task),
                    num_output_tokens=len(formatted_result),
                    total_tokens=len(task) + len(formatted_result),
                    duration_ns=0,
                )

            # Prepare structured JSON output for Galileo workflow logging
            workflow_result = {
                "agent_id": self.agent_id,
                "mode": self.mode,
                "task": task,
                "final_output": formatted_result,
                "tools_used": [result[0] for result in results],
                "execution_status": "success",
                "timestamp": datetime.now().isoformat(),
            }

            # Only call on_agent_done after all tools have completed
            if self.logger:
                await self.logger.on_agent_done(formatted_result, self.message_history)

            # Conclude the trace successfully and flush immediately
            if galileo_logger:
                galileo_logger.conclude(output=formatted_result, duration_ns=0)
                galileo_logger.flush()

            # Return structured JSON string for Galileo workflow logging
            return json.dumps(workflow_result, indent=2)

        except Exception as e:
            # Add LLM span for workflow error if logger is available
            if galileo_logger:
                galileo_logger.add_llm_span(
                    input=f"Agent workflow error",
                    output=str(e),
                    model="agent_workflow",
                    num_input_tokens=len(task),
                    num_output_tokens=len(str(e)),
                    total_tokens=len(task) + len(str(e)),
                    duration_ns=0,
                )

                # Conclude the trace with error and flush immediately
                galileo_logger.conclude(output=str(e), duration_ns=0, error=True)
                galileo_logger.flush()

            raise e
        finally:
            # Only set end_time if current_task exists
            if hasattr(self, "current_task") and self.current_task is not None:
                self.current_task.end_time = datetime.now()
                if self.current_task.status == "in_progress":
                    self.current_task.status = "completed"
            self._current_plan = None  # Clear the plan
