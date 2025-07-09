import os
import json
from galileo import (
    GalileoLogger,
)  # 🔍 Galileo import - this is the main Galileo logging library
from galileo.openai import (
    openai,
)  # 🔍 Galileo-wrapped OpenAI client for automatic logging
from typing import Dict, Any
from agent_framework.tools.base import BaseTool
from agent_framework.models import ToolMetadata
from agent_framework.llm.models import LLMMessage
from agent_framework.utils.logging import (
    get_galileo_logger,
)  # 🔍 Galileo helper import - gets centralized logger
import asyncio
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# 👀 GALILEO-WRAPPED OPENAI CLIENT: Use Galileo's OpenAI wrapper for automatic LLM logging
# This automatically logs all OpenAI API calls to Galileo with detailed metrics
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class SeriousStartupSimulatorTool(BaseTool):
    """Tool for generating serious, professional startup pitches"""

    def __init__(self):
        super().__init__()
        self.name = "serious_startup_simulator"
        self.description = "Generate a professional startup business plan based on industry, audience, and market trends"
        # 👀 GALILEO INITIALIZATION: Get the centralized Galileo logger instance
        # This ensures all tools use the same Galileo configuration and connection
        self.galileo_logger = get_galileo_logger()

    @classmethod
    def get_metadata(cls) -> ToolMetadata:
        return ToolMetadata(
            name="serious_startup_simulator",
            description="Generates professional, dry, and boring startup pitches for serious business contexts",
            tags=["startup", "generator", "business", "professional", "serious"],
            input_schema={
                "type": "object",
                "properties": {
                    "industry": {
                        "type": "string",
                        "description": "Industry for the startup",
                    },
                    "audience": {"type": "string", "description": "Target audience"},
                    "random_word": {
                        "type": "string",
                        "description": "A word to incorporate",
                    },
                    "news_context": {
                        "type": "string",
                        "description": "Recent news context for market analysis",
                    },
                },
                "required": ["industry", "audience", "random_word"],
            },
            output_schema={
                "type": "string",
                "description": "JSON string containing professional startup pitch data with metadata",
            },
        )

    async def execute(
        self, industry: str, audience: str, random_word: str, news_context: str = ""
    ) -> str:
        """Execute the serious startup simulator tool with individual Galileo trace"""

        # Log inputs as JSON
        inputs = {
            "industry": industry,
            "audience": audience,
            "random_word": random_word,
            "news_context": (
                news_context[:200] + "..." if len(news_context) > 200 else news_context
            ),
            "mode": "serious",
        }
        print(f"Serious Startup Simulator Inputs: {json.dumps(inputs, indent=2)}")

        # 👀 GALILEO LOGGER SETUP: Get the Galileo logger for this execution
        # This logger will be used to create traces and spans for observability
        logger = self.galileo_logger
        if not logger:
            print(
                "⚠️  Warning: Galileo logger not available, proceeding without logging"
            )
            # ℹ️ FALLBACK: If Galileo is not available, use the non-logging version
            return await self._execute_without_galileo(
                industry, audience, random_word, news_context
            )

        # 👀 GALILEO TRACE START: Create a new trace for this tool execution
        # A trace represents the entire lifecycle of this tool call
        # This will appear as a top-level trace in your Galileo dashboard
        trace = logger.start_trace(
            f"Serious Startup Simulator - {industry} targeting {audience}"
        )

        try:
            # 👀 GALILEO SPAN START: Add an LLM span to mark the beginning of tool execution
            # This span shows when the tool started working and what inputs it received
            logger.add_llm_span(
                input=f"Generate business plan for {industry} targeting {audience} with concept '{random_word}'",
                output="Tool execution started",
                model="serious_startup_simulator",
                num_input_tokens=len(str(inputs)),
                num_output_tokens=0,
                total_tokens=len(str(inputs)),
                duration_ns=0,
            )

            # Create the prompt with news context
            news_context_prompt = ""
            if news_context:
                news_context_prompt = f"\n\nUse these recent business news trends for market analysis:\n{news_context}"

            prompt = (
                f"Generate a professional startup business plan for a {industry} company "
                f"targeting {audience}. The plan must incorporate the concept '{random_word}' naturally. "
                f"Be formal, avoid humor, and keep it under 500 characters total."
                f"{news_context_prompt}"
            )

            # Create messages
            messages = [{"role": "user", "content": prompt}]

            # 👀 GALILEO-ENHANCED API CALL: Execute the API call using Galileo-wrapped OpenAI client
            # This automatically logs the LLM call to Galileo with detailed metrics
            # You'll see input/output tokens, model used, and response in your Galileo dashboard
            response = client.chat.completions.create(
                messages=messages,
                model="gpt-4",
                temperature=0.3,  # Lower temperature for more professional output
            )

            # Extract the response
            pitch = response.choices[0].message.content.strip()

            # Create structured output
            output = {
                "pitch": pitch,
                "character_count": len(pitch),
                "mode": "serious",
                "news_context_used": bool(news_context),
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4",
                "input_tokens": (
                    response.usage.prompt_tokens
                    if hasattr(response.usage, "prompt_tokens")
                    else 0
                ),
                "output_tokens": (
                    response.usage.completion_tokens
                    if hasattr(response.usage, "completion_tokens")
                    else 0
                ),
                "total_tokens": (
                    response.usage.total_tokens
                    if hasattr(response.usage, "total_tokens")
                    else 0
                ),
            }

            # Log output as JSON to console and for Galileo observability
            output_log = {
                "tool_execution": "serious_startup_simulator",
                "inputs": inputs,
                "output": output,
                "metadata": {
                    "character_count": output["character_count"],
                    "mode": output["mode"],
                    "news_context_used": output["news_context_used"],
                    "timestamp": output["timestamp"],
                },
            }
            print(
                f"Serious Startup Simulator Output: {json.dumps(output_log, indent=2)}"
            )

            # 👀 GALILEO SPAN COMPLETION: Add an LLM span to mark successful completion
            # This span shows the final output and completion status
            # It includes token counts and the actual result for observability
            logger.add_llm_span(
                input=f"Business plan generation completed",
                output=pitch,
                model="gpt-4",
                num_input_tokens=output["input_tokens"],
                num_output_tokens=output["output_tokens"],
                total_tokens=output["total_tokens"],
                duration_ns=0,
            )

            # 👀 GALILEO TRACE CONCLUSION: Successfully conclude the trace
            # This marks the trace as completed successfully in Galileo
            # The trace will show as "success" in your dashboard
            logger.conclude(output=pitch, duration_ns=0)
            logger.flush()

            # Return JSON string for proper Galileo logging display
            galileo_output = {
                "tool_result": "serious_startup_simulator",
                "formatted_output": json.dumps(output, indent=2),
                "pitch": output["pitch"],
                "metadata": output,
            }

            return json.dumps(galileo_output, indent=2)

        except Exception as e:
            # 👀 GALILEO ERROR HANDLING: Conclude the trace with error status
            # This marks the trace as failed in Galileo and includes the error message
            # The trace will show as "error" in your dashboard with error details
            if logger:
                logger.conclude(output=str(e), duration_ns=0, error=True)
                logger.flush()

            raise e

    async def _execute_without_galileo(
        self, industry: str, audience: str, random_word: str, news_context: str = ""
    ) -> str:
        """Fallback execution without Galileo logging"""
        # ℹ️ FALLBACK METHOD: This method runs when Galileo is not available
        # It performs the same functionality but without any observability logging
        # Create the prompt with news context
        news_context_prompt = ""
        if news_context:
            news_context_prompt = f"\n\nUse these recent business news trends for market analysis:\n{news_context}"

        prompt = (
            f"Generate a professional startup business plan for a {industry} company "
            f"targeting {audience}. The plan must incorporate the concept '{random_word}' naturally. "
            f"Be formal, avoid humor, and keep it under 500 characters total."
            f"{news_context_prompt}"
        )

        # Create messages
        messages = [{"role": "user", "content": prompt}]

        # Execute the API call
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4",
            temperature=0.3,  # Lower temperature for more professional output
        )

        # Extract the response
        pitch = response.choices[0].message.content.strip()

        # Create structured output
        output = {
            "pitch": pitch,
            "character_count": len(pitch),
            "mode": "serious",
            "news_context_used": bool(news_context),
            "timestamp": datetime.now().isoformat(),
            "model": "gpt-4",
            "input_tokens": (
                response.usage.prompt_tokens
                if hasattr(response.usage, "prompt_tokens")
                else 0
            ),
            "output_tokens": (
                response.usage.completion_tokens
                if hasattr(response.usage, "completion_tokens")
                else 0
            ),
            "total_tokens": (
                response.usage.total_tokens
                if hasattr(response.usage, "total_tokens")
                else 0
            ),
        }

        # Return JSON string for proper Galileo logging display
        galileo_output = {
            "tool_result": "serious_startup_simulator",
            "formatted_output": json.dumps(output, indent=2),
            "pitch": output["pitch"],
            "metadata": output,
        }

        return json.dumps(galileo_output, indent=2)

    def _parse_business_pitch(self, content: str) -> Dict[str, str]:
        """Parse the business pitch into structured components"""
        # This method could be enhanced to extract specific business plan sections
        # For now, it returns a simple structure
        return {
            "executive_summary": (
                content[:200] + "..." if len(content) > 200 else content
            ),
            "full_pitch": content,
        }


# ℹ️ TEST FUNCTION: This function can be used to test the tool independently
async def main():
    """Test the Serious Startup Simulator tool"""
    tool = SeriousStartupSimulatorTool()
    result = await tool.execute(
        industry="Finance",
        audience="Investors",
        random_word="fintech",
        news_context="Sample news context for testing",
    )
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
