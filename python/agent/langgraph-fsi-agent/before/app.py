"""
A demo Financial Services Agent using Chainlit and LangGraph, with Galileo as the evaluation platform.
"""

from datetime import datetime
from typing import Any
import chainlit as cl

from langchain.schema.runnable.config import RunnableConfig
from langchain_core.callbacks import Callbacks
from langchain_core.messages import HumanMessage, AIMessage

from dotenv import load_dotenv

from src.galileo_langgraph_fsi_agent.agents.supervisor_agent import (
    create_supervisor_agent,
)

# Load environment variables from .env file
load_dotenv()


# Build the agent graph
supervisor_agent = create_supervisor_agent()


@cl.on_chat_start
async def on_chat_start() -> None:
    """
    Handle the start of a chat session.

    This function is called when a new chat session starts.
    It initializes the chat with a welcome message.
    """

    # Send a welcome message to the user
    await cl.Message(
        content="Welcome to the Brahe Bank assistant! How can I help you today?"
    ).send()


@cl.on_message
async def main(msg: cl.Message) -> None:
    """
    Handle the message from the user.

    param message: The message object containing user input.
    """
    # Create a config using the current Chainlit session ID. This is linked to the memory saver in the graph
    # to allow you to continue the conversation with the same context.
    config: dict[str, Any] = {"configurable": {"thread_id": cl.context.session.id}}

    # Prepare the final answer message to stream the response back to the user
    final_answer = cl.Message(content="")

    # Build the messages dictionary with the user's message
    messages: dict[str, Any] = {"messages": [HumanMessage(content=msg.content)]}

    callbacks: Callbacks = []

    # Set up the config for the streaming response
    runnable_config = RunnableConfig(callbacks=callbacks, **config)

    # Call the graph with the user's message and stream the response back to the user
    async for response_msg in supervisor_agent.astream(
        input=messages, stream_mode="updates", config=runnable_config
    ):
        # Check for a response from the supervisor agent with the final message
        if (
            supervisor_agent.name in response_msg
            and "messages" in response_msg[supervisor_agent.name]
        ):
            # Get the last message from the supervisor's response
            message = response_msg[supervisor_agent.name]["messages"][-1]
            # If it is an AI message, then it is the final answer
            if isinstance(message, AIMessage) and message.content:
                await final_answer.stream_token(message.content)  # type: ignore

    # Send the final answer message to the user
    await final_answer.send()


# This is the entry point for running the Chainlit application used for debugging
# Otherwise to run this with hot reload, use `chainlit run app.py -w`
if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
