import os
import time
from typing import Annotated

import streamlit as st
from dotenv import load_dotenv
from galileo import galileo_context
from galileo.handlers.langchain import GalileoCallback
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from supply_chain_rag import rag_search, initialize_supply_chain_rag
from typing_extensions import TypedDict

from tools import check_supplier_compliance, assess_disruption_risk

load_dotenv()

TOOLS = [TavilySearch(max_results=2), assess_disruption_risk, check_supplier_compliance, rag_search]
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


def initialize_agent_with_rag():
    """Initialize the agent and RAG system"""
    with st.spinner("Initializing Supply Chain RAG knowledge base..."):
        try:
            # Initialize the RAG system first
            initialize_supply_chain_rag()

            # Create the agent
            agent = build_graph()
            config = {
                "configurable": {"thread_id": "1"},
                "callbacks": [GalileoCallback()]
            }

            return agent, config

        except Exception as e:
            st.error(f"Failed to initialize agent: {str(e)}")
            st.stop()


def main(session_name="Custom session name"):
    """Main function for the Streamlit app."""

    # Streamlit app title
    st.title("🔗 Supply Chain AI Agent with RAG")

    # Add sidebar with tool information
    with st.sidebar:
        st.header("🛠️ Available Tools")
        st.markdown("""
        **Supply Chain Tools:**
        - 🔍 **Web Search** - Real-time information
        - 📊 **Risk Assessment** - Evaluate disruption risks
        - ✅ **Compliance Check** - Supplier compliance status
        - 📚 **Knowledge Base** - Supply chain expertise

        **RAG Knowledge Areas:**
        - Supply Chain Fundamentals
        - Risk Management
        - Supplier Evaluation
        - Logistics & Transportation
        - Inventory Management
        - Technology in Supply Chain
        - Sustainability & ESG
        - Compliance & Regulations
        """)

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False

    # Initialize the agent if not already done
    if not st.session_state.agent_initialized:
        with st.spinner("Initializing AI agent..."):
            galileo_context.start_session(name=session_name)
            st.session_state.agent, st.session_state.config = initialize_agent_with_rag()
            st.session_state.tools = TOOLS
            st.session_state.agent_initialized = True

    # Display chat history
    display_chat_history()

    # Add example queries
    if not st.session_state.messages:
        st.markdown("### 💡 Try these example queries:")
        examples = [
            "What are the key components of supply chain risk management?",
            "How do I evaluate supplier performance?",
            "What are the main transportation modes and their characteristics?",
            "Check compliance status for supplier SUP001",
            "Assess disruption risk for semiconductors in Southeast Asia"
        ]

        for example in examples:
            if st.button(example, key=f"example_{hash(example)}"):
                # Add user message to chat history
                user_message = HumanMessage(content=example)
                st.session_state.messages.append(user_message)

                # Display the user message immediately
                with st.chat_message("user"):
                    st.write(example)

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

                st.rerun()

    # Add chat input
    user_input = st.chat_input("Ask me anything about supply chain management...")

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
