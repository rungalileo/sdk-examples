import os
import json
import warnings
from galileo import log, galileo_context, openai as galileo_openai
from dotenv import load_dotenv
from rich.console import Console
import questionary
import openai

# Suppress Pydantic serializer warnings
warnings.filterwarnings("ignore", message="Pydantic serializer warnings")

load_dotenv()
console = Console()
client = galileo_openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# Tool: Convert text numbers to numerical values
@log(span_type="tool", name="convert_text_to_arithmetic_expression")
def convert_text_to_arithmetic_expression(text):
    """Convert a text number (like 'seven') to its numerical value (7)."""
    console.print(f"Converting: {text}")

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"Convert the expression {text} with text numbers to a valid arithmetic expression. Respond with only the arithmetic expression.",
            }
        ],
    )

    result = response.choices[0].message.content.strip()
    try:
        expression = result
        console.print(f"Converted to: {expression}")
        return str(expression)
    except:
        console.print(f"Error parsing: {result}")
        return "Error"


# Tool: Calculator for arithmetic operations
@log(span_type="tool", name="calculate")
def calculate(expression):
    """Perform a calculation based on the given expression."""
    console.print(f"Calculating: {expression}")

    try:
        result = eval(expression)
        console.print(f"Result: {result}")
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


# Load tools from tools.json
def get_tools():
    with open(os.path.join(os.path.dirname(__file__), "tools.json"), "r") as f:
        return json.load(f)


# Main processing function
@log(span_type="llm")
def process_query(query):
    """Process a numerical query using LLM and tools."""
    console.print(f"Processing query: {query}")

    # Initialize conversation history with serializable dictionaries
    messages = [
        {
            "role": "system",
            "content": "Convert text expressions to valid arithmetic expressions, then calculate results. Use tools one at a time.",
        },
        {"role": "user", "content": f"Process this query: '{query}'"},
    ]

    tools = get_tools()
    results = []

    # Agent loop - continue until the LLM decides we're done
    while True:
        # Get next tool call from LLM
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
        )

        # Convert the assistant message to a serializable dictionary
        assistant_message = response.choices[0].message
        assistant_dict = {"role": "assistant", "content": assistant_message.content}

        # Add tool calls if present
        if assistant_message.tool_calls:
            tool_calls_list = []
            for tool_call in assistant_message.tool_calls:
                tool_calls_list.append(
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                )
            assistant_dict["tool_calls"] = tool_calls_list

        messages.append(assistant_dict)  # Add assistant's response to history

        # Check if LLM is done (no more tool calls)
        if not assistant_message.tool_calls:
            # LLM provided a final answer
            if assistant_message.content:
                results.append(assistant_message.content)
            break

        # Process the tool call
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            console.print(f"\n[bold]Executing {function_name} tool:[/bold]")

            # Execute the appropriate tool
            if function_name == "convert_text_to_arithmetic_expression":
                text = function_args["text"]
                result = convert_text_to_arithmetic_expression(text)
            elif function_name == "calculate":
                expression = function_args["expression"]
                result = calculate(expression)
            else:
                result = f"Unknown tool: {function_name}"

            # Add the tool result to conversation history as a serializable dictionary
            tool_result_message = {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": result,
            }
            messages.append(tool_result_message)
            results.append(result)

    # Create a summary
    if results:
        summary = "\n".join(results)
    else:
        summary = "No results produced."

    return summary


def main():
    console.print("[bold]Minimal Number Converter & Calculator[/bold]")

    query = questionary.text("Enter your query:", default="What's 4 + seven?").ask()

    if query is None or query.lower() in ["exit", "quit", "q"]:
        console.print("Exiting.")
        return

    # Process the query within a Galileo context
    with galileo_context():
        result = process_query(query)

    console.print("\n[bold green]Result:[/bold green]")
    console.print(result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\nExiting.")
