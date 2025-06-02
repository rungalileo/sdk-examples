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

from galileo import GalileoLogger, galileo_context
from galileo.handlers.langchain import GalileoAsyncCallback

from src.galileo_langgraph_fsi_agent.agents.supervisor_agent import create_supervisor_agent

# Load environment variables from .env file
load_dotenv()

# Initialize the Galileo logger
galileo_logger = GalileoLogger()


# Build the agent graph
supervisor_agent = create_supervisor_agent()


@cl.on_chat_start
async def on_chat_start() -> None:
    """
    Handle the start of a chat session.

    This function is called when a new chat session starts.
    It initializes the chat with a welcome message.
    """
    create_galileo_session()

    # Send a welcome message to the user
    await cl.Message(content="Welcome to the Brahe Bank assistant! How can I help you today?").send()


def create_galileo_session():
    try:
        # Start Galileo session with unique session name
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_name = f"FSI Agent - {current_time}"
        galileo_context.start_session(name=session_name, external_id=cl.context.session.id)

        # Create the callback. This needs to be created in the same thread as the session
        # so that it uses the same session context.
        galileo_callback = GalileoAsyncCallback()
        cl.user_session.set("galileo_callback", galileo_callback)

        # Store session info in user session for later use
        cl.user_session.set("galileo_session_started", True)
        cl.user_session.set("session_name", session_name)

        print(f"✅ Galileo session started: {session_name}")

    except Exception as e:
        print(f"❌ Failed to start Galileo session: {str(e)}")
        # Continue without Galileo rather than failing completely
        cl.user_session.set("galileo_session_started", False)


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

    # Create a callback handler to log the response to Galileo
    callbacks: Callbacks = []
    if cl.user_session.get("galileo_session_started", False):
        galileo_callback = cl.user_session.get("galileo_callback")
        callbacks: Callbacks = [galileo_callback]  # type: ignore
    else:
        print("Galileo session not started, using default callbacks.")

    # Set up the config for the streaming response
    runnable_config = RunnableConfig(callbacks=callbacks, **config)

    # Call the graph with the user's message and stream the response back to the user
    async for response_msg in supervisor_agent.astream(input=messages, stream_mode="updates", config=runnable_config):
        # Check for a response from the supervisor agent with the final message
        if supervisor_agent.name in response_msg and "messages" in response_msg[supervisor_agent.name]:
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
