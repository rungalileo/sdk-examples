import json
import logging
from typing import Any

from dotenv import load_dotenv

# Use Galileo's wrapped OpenAI client to automatically log all API calls.
# This is a drop-in replacement for the standard `openai` module.
from galileo import openai

load_dotenv()

logging.basicConfig(level=logging.INFO)

# Create an OpenAI client. Because we imported from `galileo`, all calls
# made through this client are automatically instrumented and logged.
client = openai.OpenAI()

# Define the tools that will be available to the model. Each tool is a
# function definition that the model can choose to call based on the user's query.
tools: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit",
                },
            },
            "required": ["location"],
        },
    },
    {
        "type": "function",
        "name": "get_stock_price",
        "description": "Get the current stock price for a given ticker symbol",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock ticker symbol, e.g. AAPL, GOOGL, MSFT",
                },
            },
            "required": ["symbol"],
        },
    },
]


# --- Simulated tool implementations ---
# In a real application, these would call external APIs or services.


def get_weather(location: str, unit: str = "fahrenheit") -> str:
    """Simulated weather function that returns a hardcoded temperature."""
    return json.dumps({"location": location, "temperature": 72, "unit": unit})


def get_stock_price(symbol: str) -> str:
    """Simulated stock price function that returns a hardcoded price."""
    prices = {"AAPL": 178.50, "GOOGL": 141.25, "MSFT": 378.90, "AMZN": 153.40}
    price = prices.get(symbol.upper(), 100.00)
    return json.dumps({"symbol": symbol.upper(), "price": price, "currency": "USD"})


def main():
    user_message = "What's the weather like in San Francisco and what's the current stock price of Apple?"
    input_list = []

    # Step 1: Send the user message to the model along with the available tools.
    # The model will analyze the query and decide which tools to call.
    response = client.responses.create(
        model="gpt-4o-mini",
        input=user_message,
        tools=tools,  # type: ignore[arg-type]
        # reasoning={"effort": "high"},
    )

    # Step 2: Collect the model's output (which includes function_call items)
    # into the input list for the next request.
    input_list += response.output

    # Step 3: Iterate over the model's output and execute any requested tool calls.
    # Each function_call item contains the function name and its arguments.
    for item in response.output:
        if item.type == "function_call":
            if item.name == "get_weather":
                weather = get_weather(**json.loads(item.arguments))

                # Append the tool result back to the input list so the model
                # can use it in the next turn. The call_id links the output
                # back to the original function call.
                input_list.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps({"weather": weather}),
                    }
                )
            if item.name == "get_stock_price":
                stock_price = get_stock_price(**json.loads(item.arguments))
                input_list.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps({"stock_price": stock_price}),
                    }
                )

    print("Final input:")
    print(input_list)

    # Step 4: Send the conversation history (including tool call results) back
    # to the model. The model will now generate a natural language response
    # that incorporates the tool outputs.
    response = client.responses.create(
        model="gpt-5",
        instructions="Respond using the results provided to you by the tools.",
        tools=tools,  # pyright: ignore[reportArgumentType]
        input=input_list,
        reasoning={"effort": "high", "summary": "detailed"},
    )

    # Step 5: Print the final response from the model.
    print("Final output:")
    print(response.model_dump_json(indent=2))
    print("\n" + response.output_text)


if __name__ == "__main__":
    main()
