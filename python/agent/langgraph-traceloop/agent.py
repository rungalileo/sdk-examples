import os
from typing import TypedDict, Annotated
import dotenv

import openai
from langgraph.graph import END, StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client for tool usage
client = openai.OpenAI(api_key=openai_api_key)
print("OpenAI client configured")


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================


@tool
def validate_input_tool(user_input: str) -> str:
    """
    Validates and prepares the user input for processing.

    Args:
        user_input: The user's input question to validate

    Returns:
        The validated user input
    """
    print(f"[TOOL] Validating input: '{user_input}'")

    if not user_input or len(user_input.strip()) == 0:
        return "Error: Empty input provided"

    return user_input.strip()


@tool
def generate_response_tool(user_input: str) -> str:
    """
    Generates a response from OpenAI based on the user input.

    Args:
        user_input: The validated user input question

    Returns:
        The LLM's response to the question
    """
    try:
        print(f"[TOOL] Calling OpenAI with: '{user_input}'")

        # Make the OpenAI API call - Traceloop automatically traces this
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}],
            max_tokens=300,
            temperature=0.7,
        )

        # Extract the response content
        llm_response = response.choices[0].message.content

        if not llm_response:
            print("No response from OpenAI")
            return "Error: No response from OpenAI"
        else:
            print(f"Received response: '{llm_response[:100]}...'")

        return llm_response

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return f"Error: {str(e)}"


@tool
def format_answer_tool(llm_response: str) -> str:
    """
    Formats and cleans up the LLM response into a concise answer.

    Args:
        llm_response: The raw response from the LLM

    Returns:
        A formatted and cleaned answer
    """
    print(f"[TOOL] Formatting answer from: '{llm_response[:50]}...'")

    # Simple parsing - extract first sentence for a concise answer
    sentences = llm_response.split(". ")
    parsed_answer = sentences[0] if sentences else llm_response

    # Clean up the answer
    parsed_answer = parsed_answer.strip()
    if not parsed_answer.endswith(".") and parsed_answer:
        parsed_answer += "."

    print(f"Parsed answer: '{parsed_answer}'")

    return parsed_answer


# List of all available tools
tools = [validate_input_tool, generate_response_tool, format_answer_tool]


# ============================================================================
# STATE DEFINITION
# ============================================================================


class AgentState(TypedDict):
    # The add_messages reducer handles message list updates properly
    # It ensures messages are appended correctly without duplication
    messages: Annotated[list[BaseMessage], add_messages]


# ============================================================================
# NODE FUNCTIONS
# ============================================================================


def agent_node(state: AgentState):
    """
    The agent node that decides which tools to call.
    """
    messages = state["messages"]

    # Initialize the LLM with tool calling capabilities
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    # Get the agent's response
    response = llm_with_tools.invoke(messages)

    print(f"Agent response: {response}")

    # Return just the new message - add_messages reducer will append it
    return {"messages": [response]}


def should_continue(state: AgentState):
    """
    Determines whether to continue with tool calls or end.
    """
    messages = state["messages"]
    last_message = messages[-1]

    # If there are tool calls, continue to the tools node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Otherwise, end the workflow
    return "end"


# ============================================================================
# AGENT FACTORY
# ============================================================================


def create_agent():
    """
    Creates an agent that uses tools to process requests.
    This demonstrates the tool-calling pattern in LangGraph.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        },
    )

    # After tools are called, go back to the agent
    workflow.add_edge("tools", "agent")

    # Compile the workflow
    app = workflow.compile()

    return app
