import os
import time
from typing import Annotated

import streamlit as st
from dotenv import load_dotenv
from galileo import galileo_context
from galileo.handlers.langchain import GalileoCallback
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from tools import check_supplier_compliance, assess_disruption_risk

load_dotenv()

TOOLS = [TavilySearch(max_results=2), assess_disruption_risk, check_supplier_compliance]
llm_with_tools = ChatOpenAI(model="gpt-4").bind_tools(TOOLS)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def invoke_chatbot(state):
    """Create an LLM with the specified tools."""
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


def build_graph() -> CompiledStateGraph:
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", invoke_chatbot)

    # Set up tool node
    tool_node = ToolNode(tools=TOOLS)
    graph_builder.add_node("tools", tool_node)

    # Set up graph edges
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    return graph_builder.compile()

def display_chat_history():
    """Display all messages in the chat history."""
    if not st.session_state.messages:
        return
        
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)
        else:
            print("!!!!!! OTHER MESSAGE TYPE:")
            print(message)



def main(session_name="Custom session name"):
    """Main function for the Streamlit app."""

    # Streamlit app title
    st.title("LangGraph AI Agent")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False

    # Initialize the agent if not already done
    if not st.session_state.agent_initialized:
        with st.spinner("Initializing AI agent..."):
            galileo_context.start_session(name=session_name)
            # Create the agent
            st.session_state.agent = build_graph()
            RunnableConfig()
            st.session_state.config = {"configurable": {"thread_id": "1"}, "callbacks": [GalileoCallback()]}
            st.session_state.tools = TOOLS
            st.session_state.agent_initialized = True

    # Display chat history
    display_chat_history()

    # Add chat input
    user_input = st.chat_input("Type your message here...")
    
    # Process user input when submitted
    if user_input:
        # Add user message to chat history
        user_message = HumanMessage(content=user_input)
        st.session_state.messages.append(user_message)
        
        # Display the user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get response from agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Run the agent with the user message
                result = st.session_state.agent.invoke(
                    {"messages": user_message},
                    config=st.session_state.config
                )
                
                # Get the latest AI message
                ai_message = result["messages"][-1]
                st.session_state.messages.append(ai_message)
                st.write(ai_message.content)


if __name__ == "__main__":
    os.environ["GALILEO_PROJECT"] = "langgraph-demo1-test"
    os.environ["GALILEO_LOG_STREAM"] = "dev"
    main(session_name=f"Test Chat- {int(time.time())}")
