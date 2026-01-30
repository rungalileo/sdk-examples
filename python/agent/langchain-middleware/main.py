import json
import os

from dotenv import load_dotenv
from galileo import galileo_context
from galileo.handlers.langchain.middleware import GalileoMiddleware
from langchain.agents.factory import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# Load environment variables (e.g., API keys)
load_dotenv()

# Initialize the OpenAI chat model that the agent will use for reasoning
model = ChatOpenAI(
    name="gpt-5",
    api_key=os.getenv("OPENAI_API_KEY"),  # type: ignore
)


# Define a tool that allows the agent to get weather information
# The @tool decorator converts this function into a LangChain tool that the agent can use
@tool
def get_weather(location: str, unit: str = "fahrenheit") -> str:
    """Get the current weather for a given location."""
    # In a real application, this would call a weather API
    # For demonstration, we return mock data
    return json.dumps({"location": location, "temperature": 72, "unit": unit})


# Define a tool that allows the agent to get stock price information
@tool
def get_stock_price(symbol: str) -> str:
    """Get the current stock price for a given ticker symbol."""
    # Mock stock prices for demonstration
    prices = {"AAPL": 178.50, "GOOGL": 141.25, "MSFT": 378.90, "AMZN": 153.40}
    price = prices.get(symbol.upper(), 100.00)
    return json.dumps({"symbol": symbol.upper(), "price": price, "currency": "USD"})


def main() -> None:
    # Use the Galileo context manager to specify project and log stream
    # All traces created within this context will be associated with this project
    with galileo_context(project=os.getenv("GALILEO_PROJECT", "langchain-middleware"), log_stream=os.getenv("GALILEO_LOG_STREAM", "agent_execution")):
        # Create an agent with GalileoMiddleware for automatic logging
        # GalileoMiddleware automatically captures:
        # - Agent lifecycle events (start/completion)
        # - Model calls (prompts, responses, metadata)
        # - Tool calls (function names, arguments, outputs)
        agent = create_agent(
            model,  # The LLM the agent uses for reasoning
            tools=[get_weather, get_stock_price],  # Available tools
            middleware=[GalileoMiddleware()],  # Add GalileoMiddleware for automatic logging
        )

        # Invoke the agent with a question that requires using both tools
        # The agent will:
        # 1. Understand it needs weather info for San Francisco
        # 2. Call the get_weather tool
        # 3. Understand it needs Apple's stock price
        # 4. Call the get_stock_price tool
        # 5. Synthesize the results into a coherent response
        result = agent.invoke({"messages": [HumanMessage(content="What's the weather like in San Francisco and what's the current stock price of Apple?")]})
        print(f"\nAgent Response:\n{result}")


if __name__ == "__main__":
    main()
