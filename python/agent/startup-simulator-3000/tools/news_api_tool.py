import os
import json
import aiohttp
from galileo import (
    GalileoLogger,
)  # 🔍 Galileo import - this is the main Galileo logging library
from galileo import log  # 🔍 Galileo decorator import for tool spans
from typing import Dict, Any, List
from agent_framework.tools.base import BaseTool
from agent_framework.models import ToolMetadata
from agent_framework.utils.logging import (
    get_galileo_logger,
)  # 🔍 Galileo helper import - gets centralized logger
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()


class NewsAPITool(BaseTool):
    """Tool for fetching business news from NewsAPI"""

    def __init__(self):
        super().__init__()
        self.name = "news_api_tool"
        self.description = "Fetch business news from NewsAPI for market analysis"
        # 👀 GALILEO INITIALIZATION: Get the centralized Galileo logger instance
        # This ensures all tools use the same Galileo configuration and connection
        self.galileo_logger = get_galileo_logger()

    @classmethod
    def get_metadata(cls) -> ToolMetadata:
        return ToolMetadata(
            name="news_api_tool",
            description="Fetches business news from NewsAPI for market analysis and professional context",
            tags=["news", "business", "market", "analysis"],
            input_schema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "News category to fetch",
                        "default": "business",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of articles to fetch",
                        "default": 5,
                    },
                },
                "required": [],
            },
            output_schema={
                "type": "string",
                "description": "JSON string containing news articles with metadata",
            },
        )

    # 👀 GALILEO TOOL SPAN DECORATOR: This decorator creates a tool span for HTTP API calls
    # Since this tool makes HTTP requests to NewsAPI (not LLM calls), we use span_type="tool"
    # The name "Tool-NewsAPI" will appear in your Galileo dashboard as a tool span
    @log(span_type="tool", name="Tool-NewsAPI")
    async def execute(self, category: str = "business", limit: int = 5) -> str:
        """Fetch business news from NewsAPI"""

        # Log inputs
        inputs = {
            "category": category,
            "limit": limit,
            "timestamp": datetime.now().isoformat(),
        }
        print(f"News API Tool Inputs: {json.dumps(inputs, indent=2)}")

        # 👀 GALILEO LOGGER SETUP: Get the Galileo logger for this execution
        # This logger will be used to create traces and spans for observability
        logger = self.galileo_logger
        if not logger:
            print("⚠️  Warning: Galileo logger not available, proceeding without logging")
            # ℹ️ FALLBACK: If Galileo is not available, use the non-logging version
            return await self._execute_without_galileo(category, limit)

        # 👀 GALILEO TRACE START: Create a new trace for this tool execution
        # A trace represents the entire lifecycle of this tool call
        # This will appear as a top-level trace in your Galileo dashboard
        trace = logger.start_trace(f"News API Tool - Fetching {category} news")

        try:
            # 🔧 TOOL EXECUTION: This tool makes HTTP API calls to NewsAPI
            # Since it's not an LLM call, we don't need LLM spans here
            # The @log decorator above automatically creates the tool span

            # Get API key from environment
            api_key = os.environ.get("NEWS_API_KEY")
            if not api_key:
                raise Exception("NEWS_API_KEY not found in environment variables")

            # Fetch news from NewsAPI
            url = f"https://newsapi.org/v2/top-headlines"
            params = {
                "country": "us",
                "category": category,
                "apiKey": api_key,
                "pageSize": limit,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch news: {response.status}")

                    data = await response.json()

                    if data.get("status") != "ok":
                        raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")

                    articles = data.get("articles", [])

                    # Format articles for context
                    formatted_articles = []
                    for article in articles[:limit]:
                        title = article.get("title", "No title")
                        description = article.get("description", "No description")
                        source = article.get("source", {}).get("name", "Unknown source")
                        formatted_articles.append(f"• {title} ({source}) - {description}")

                    context = "\n".join(formatted_articles)

            # Create structured output
            output = {
                "articles": articles[:limit],
                "formatted_context": context,
                "article_count": len(articles[:limit]),
                "requested_limit": limit,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "source": "newsapi",
            }

            # Log output as JSON
            output_log = {
                "tool_execution": "news_api_tool",
                "inputs": inputs,
                "output": output,
                "metadata": {
                    "article_count": output["article_count"],
                    "requested_limit": output["requested_limit"],
                    "category": output["category"],
                    "timestamp": output["timestamp"],
                },
            }
            print(f"News API Tool Output: {json.dumps(output_log, indent=2)}")

            # 👀 GALILEO TRACE CONCLUSION: Successfully conclude the trace
            # This marks the trace as completed successfully in Galileo
            # The trace will show as "success" in your dashboard
            logger.conclude(output=context, duration_ns=0)

            # Return JSON string for proper Galileo logging display
            galileo_output = {
                "tool_result": "news_api_tool",
                "formatted_output": json.dumps(output, indent=2),
                "context": context,
                "metadata": output,
            }

            return json.dumps(galileo_output, indent=2)

        except Exception as e:
            # 👀 GALILEO ERROR HANDLING: Conclude the trace with error status
            # This marks the trace as failed in Galileo and includes the error message
            # The trace will show as "error" in your dashboard with error details
            if logger:
                logger.conclude(output=str(e), duration_ns=0, error=True)

            raise e

    async def _execute_without_galileo(self, category: str = "business", limit: int = 5) -> str:
        """Fallback execution without Galileo logging"""
        # ℹ️ FALLBACK METHOD: This method runs when Galileo is not available
        # It performs the same functionality but without any observability logging
        # Get API key from environment
        api_key = os.environ.get("NEWS_API_KEY")
        if not api_key:
            raise Exception("NEWS_API_KEY not found in environment variables")

        # Fetch news from NewsAPI
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            "country": "us",
            "category": category,
            "apiKey": api_key,
            "pageSize": limit,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch news: {response.status}")

                data = await response.json()

                if data.get("status") != "ok":
                    raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")

                articles = data.get("articles", [])

                # Format articles for context
                formatted_articles = []
                for article in articles[:limit]:
                    title = article.get("title", "No title")
                    description = article.get("description", "No description")
                    source = article.get("source", {}).get("name", "Unknown source")
                    formatted_articles.append(f"• {title} ({source}) - {description}")

                context = "\n".join(formatted_articles)

        # Create structured output
        output = {
            "articles": articles[:limit],
            "formatted_context": context,
            "article_count": len(articles[:limit]),
            "requested_limit": limit,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "source": "newsapi",
        }

        # Return JSON string for proper Galileo logging display
        galileo_output = {
            "tool_result": "news_api_tool",
            "formatted_output": json.dumps(output, indent=2),
            "context": context,
            "metadata": output,
        }

        return json.dumps(galileo_output, indent=2)


# ℹ️ TEST FUNCTION: This function can be used to test the tool independently
async def main():
    """Test the News API tool"""
    tool = NewsAPITool()
    result = await tool.execute(category="business", limit=3)
    print(f"Result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
