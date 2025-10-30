"""
A sample application that shows how to log MCP server calls as tool spans.

This code is described in the Log MCP Server Tool Calls how-to guide in the Galileo documentation:
https://v2docs.galileo.ai/how-to-guides/basics/log-mcp-server-calls/log-mcp-server-calls
"""

import asyncio
import os

from datetime import datetime

from anthropic import Anthropic, omit
from anthropic.types import Message

from dotenv import load_dotenv

from galileo import galileo_context

from mcp_client import MCPClient

load_dotenv()  # load environment variables from .env

anthropic = Anthropic()
message_history = []
mcp_client = MCPClient()


def call_llm(messages, use_tools: bool = True) -> Message:
    """
    Call the LLM with the provided query and return
    the response text
    """
    galileo_logger = galileo_context.get_logger_instance()

    # Capture the current time in nanoseconds for logging
    start_time_ns = datetime.now().timestamp() * 1_000_000_000

    # Call the LLM
    response = anthropic.messages.create(
        model=os.environ["ANTHROPIC_MODEL"],
        max_tokens=1000,
        messages=messages,
        tools=mcp_client.tools if use_tools else omit,
    )

    # Log the LLM call
    for content in [c for c in response.content if c.type == "text"]:
        galileo_logger.add_llm_span(
            input=messages,
            output=content.text,
            model=os.environ["ANTHROPIC_MODEL"],
            num_input_tokens=response.usage.input_tokens,
            num_output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens
            + response.usage.output_tokens,
            duration_ns=int(
                (datetime.now().timestamp() * 1_000_000_000) - start_time_ns
            ),
        )

    return response


async def process_query(query: str) -> str:
    """Process a query using Claude"""
    # Capture the current time in nanoseconds for logging
    start_time_ns = datetime.now().timestamp() * 1_000_000_000

    # Start a Galileo Logger trace
    galileo_logger = galileo_context.get_logger_instance()
    galileo_logger.start_trace(
        input=query,
        name="MCP Chatbot Query",
    )

    message_history.append({"role": "user", "content": query})

    # Call the LLM
    response = call_llm(message_history)

    # Process the response
    final_text = []

    for content in response.content:
        if content.type == "text":
            # Save the text response to the message history
            message_history.append(
                {"role": "assistant", "content": content.text}
            )
            final_text.append(content.text)
        elif content.type == "tool_use":
            # Get the tool start time
            tool_start_time_ns = datetime.now().timestamp() * 1_000_000_000

            # Execute tool call
            result = await mcp_client.call_tool(content.name, content.input)

            # Log the tool call
            galileo_logger.add_tool_span(
                input=query,
                output=result.content[0].text,
                name=content.name,
                tool_call_id=content.id,
                duration_ns=int(
                    (datetime.now().timestamp() * 1_000_000_000)
                    - tool_start_time_ns
                ),
            )

            final_text.append(
                f"[Calling tool {content.name}" + f"with args {content.input}]"
            )

            # Create a copy of the messages
            # And add the tool response
            messages = message_history.copy()
            if hasattr(content, "text") and content.text:
                messages.append({"role": "assistant", "content": content.text})
            messages.append({"role": "user", "content": result.content})

            # Call the LLM without tools for the final response
            response = call_llm(messages, use_tools=False)

            # Add the response to the original message history
            message_history.append(
                {"role": "assistant", "content": response.content[0].text}
            )

            final_text.append(response.content[0].text)

    # Conclude and flush the trace
    galileo_logger.conclude(
        output="\n".join(final_text),
        duration_ns=int(
            (datetime.now().timestamp() * 1_000_000_000) - start_time_ns
        ),
    )
    galileo_logger.flush()

    # Return the final response text
    return "\n".join(final_text)


async def main():
    """Main function to run the chat loop"""
    # Connect to the MCP server
    await mcp_client.connect_to_server()

    # Start a Galileo Logger session
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    galileo_context.start_session(f"MCP Chatbot Session - {current_time}")

    while True:
        query = input("\nQuery: ").strip()
        if query.lower() == "quit":
            break

        print(await process_query(query))


if __name__ == "__main__":
    asyncio.run(main())
