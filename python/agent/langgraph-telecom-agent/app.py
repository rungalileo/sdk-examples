"""
A demo Telecom Customer Service Agent using Chainlit and LangGraph, with Galileo as the evaluation platform.
"""

from datetime import datetime
from typing import Any
import chainlit as cl

from langchain.schema.runnable.config import RunnableConfig
from langchain_core.callbacks import Callbacks
from langchain_core.messages import HumanMessage, AIMessage

from dotenv import load_dotenv

from galileo import galileo_context
from galileo.handlers.langchain import GalileoAsyncCallback

from src.agents.supervisor_agent import (
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
    create_galileo_session()


def create_galileo_session():
    """
    Create a new Galileo session for tracking user interactions.

    This session is then stored in the Chainlit user session for later use.
    """
    try:
        # Initialize Galileo context first
        galileo_context.init()
        # Start Galileo session with unique session name
        galileo_context.start_session(name="Telecom Agent", external_id=cl.context.session.id)

        # Create the callback. This needs to be created in the same thread as the session
        # so that it uses the same session context.
        galileo_callback = GalileoAsyncCallback()
        cl.user_session.set("galileo_callback", galileo_callback)

        # Store session info in user session for later use
        cl.user_session.set("galileo_session_started", True)

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

    # Track agent steps for visibility
    current_agent = None
    current_step = None
    step_counter = 0

    # Debug: Log that we're starting
    print(f"Starting to process message: {msg.content[:50]}...")

    # Create main processing step
    async with cl.Step(name="🎯 Processing Request", type="run", show_input=True) as main_step:
        main_step.input = msg.content

        # Call the graph with the user's message and stream the response back to the user
        async for response_msg in supervisor_agent.astream(input=messages, stream_mode="updates", config=runnable_config):
            # Debug: Log the response structure
            print(f"Response keys: {response_msg.keys()}")

            # Detect which agent is being called
            for agent_name in response_msg.keys():
                # Skip system nodes
                if agent_name in ["__start__", "__end__", supervisor_agent.name]:
                    continue

                # New agent detected - create a step for it
                if agent_name and agent_name != current_agent:
                    # Close previous step if exists
                    if current_step:
                        current_step.output = "✅ Completed"
                        await current_step.update()

                    # Create new step for this agent
                    step_counter += 1
                    agent_display_name = agent_name.replace("-", " ").replace("_", " ").title()

                    current_step = cl.Step(name=f"Step {step_counter}: {agent_display_name}", type="tool")
                    current_step.input = "Processing..."
                    await current_step.send()
                    current_agent = agent_name

                    # Show what the agent is doing
                    if "messages" in response_msg[agent_name]:
                        agent_messages = response_msg[agent_name]["messages"]
                        if agent_messages:
                            last_msg = agent_messages[-1]
                            if hasattr(last_msg, "content") and last_msg.content:
                                current_step.output = f"Working: {last_msg.content[:100]}..."
                                await current_step.update()

            # Check for supervisor's routing decision
            if supervisor_agent.name in response_msg:
                if "next" in response_msg[supervisor_agent.name]:
                    next_agent = response_msg[supervisor_agent.name]["next"]
                    if next_agent and next_agent != "__end__":
                        # Show routing decision
                        routing_step = cl.Step(
                            name=f"🔀 Routing to {next_agent.replace('-', ' ').title()}",
                            type="llm",
                        )
                        routing_step.input = "Analyzing request and routing..."
                        routing_step.output = f"Selected: {next_agent}"
                        await routing_step.send()

            # Check for a response from the supervisor agent with the final message
            if supervisor_agent.name in response_msg and "messages" in response_msg[supervisor_agent.name]:
                # Get the last message from the supervisor's response
                message = response_msg[supervisor_agent.name]["messages"][-1]
                # If it is an AI message, then it is the final answer
                if isinstance(message, AIMessage) and message.content:
                    # Close any open step
                    if current_step:
                        current_step.output = "✅ Completed"
                        await current_step.update()

                    # Create final response step
                    response_step = cl.Step(name="📝 Final Response", type="llm")
                    response_step.input = "Generating response..."
                    await response_step.send()

                    # Stream the response
                    await final_answer.stream_token(message.content)  # type: ignore

                    response_step.output = "Response delivered"
                    await response_step.update()

        main_step.output = "✅ Request completed"

    # Send the final answer message to the user
    await final_answer.send()


# This is the entry point for running the Chainlit application used for debugging
# Otherwise to run this with hot reload, use `chainlit run app.py -w`
if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
