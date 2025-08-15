import os
import time
import uuid

import streamlit as st
from dotenv import load_dotenv
from galileo import galileo_context
from galileo.handlers.langchain import GalileoCallback
from langchain_core.messages import AIMessage, HumanMessage

from financial_agent import FinancialAgentRunner
from orchestrator import ModularMultiAgentOrchestrator
from supply_chain_agent import SupplyChainAgentRunner

load_dotenv()

def display_chat_history():
    """Display all messages in the chat history with agent attribution."""
    if not st.session_state.messages:
        return

    for message_data in st.session_state.messages:
        if isinstance(message_data, dict):
            message = message_data.get("message")

            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message.content)
        else:
            # Fallback for old message format
            if isinstance(message_data, HumanMessage):
                with st.chat_message("user"):
                    st.write(message_data.content)
            elif isinstance(message_data, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message_data.content)


def show_example_queries(query_1: str, query_2: str):
    """Show example queries demonstrating the modular system"""
    st.subheader("Example queries")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(query_1, key="query_1"):
            return query_1

    with col2:
        if st.button(query_2, key="query_2"):
            return query_2
    return None


def display_workflow_info(routing_decision):
    """Display information about the workflow being executed"""
    if routing_decision.get("requires_collaboration", False):
        st.info(f"""
        🔄 **Multi-Agent Workflow with Translation**

        **Flow:** Intent Classifier → {' → '.join(routing_decision['execution_order'][:-1])} → Translation Fork → Final Response
        """)
    else:
        agent_name = routing_decision.get("primary_agent", "unknown").replace("_agent", "")
        st.info(f"""
        🎯 **Single Agent Workflow with Translation**

        **Flow:** Intent Classifier → {agent_name.title()} Agent → Translation Fork → Multilingual Response
        """)


def get_welcome_message():
    """Get the updated welcome message with translation info"""
    return AIMessage(content="Welcome to the Modular Multi-Agent Supply Chain System!")


def show_multilingual_progress():
    """Show progress for multilingual workflows"""
    progress_bar = st.progress(0)
    status_text = st.empty()

    steps = [
        "Intent Classification",
        "Supply Chain Analysis",
        "Financial Analysis",
        "Synthesis",
        "Spanish Translation",
        "Hindi Translation",
        "Multilingual Combination"
    ]

    for i, step in enumerate(steps):
        progress = (i + 1) / len(steps)
        progress_bar.progress(progress)

        if step in ["Spanish Translation", "Hindi Translation"]:
            status_text.text(f"🌍 {step}...")
        else:
            status_text.text(f"🧩 {step}...")

        time.sleep(0.6)

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()


def orchestrate_streamlit_and_get_user_input(
    agent_title: str,
    example_query_1: str,
    example_query_2: str
):
    # App title and description
    st.title(agent_title)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        session_id = str(uuid.uuid4())[:10]
        st.session_state.session_id = session_id
        try:
            galileo_context.start_session(external_id=session_id)
        except Exception as e:
            st.error(f"Failed to start Galileo session: {str(e)}")
            st.stop()
        # Add welcome message
        welcome_message = AIMessage(content="Welcome!")
        st.session_state.messages.append({
            "message": welcome_message,
            "agent": "system"
        })

    # Show example queries
    example_query = show_example_queries(example_query_1, example_query_2)

    # Display chat history
    display_chat_history()

    # Get user input
    user_input = st.chat_input("How can I help you?...")
    # Use example query if button was clicked
    if example_query:
        user_input = example_query
    return user_input


def process_input_for_simple_app(user_input: str|None):
    if user_input:
        # Add user message to chat history
        user_message = HumanMessage(content=user_input)
        st.session_state.messages.append({
            "message": user_message,
            "agent": "user"
        })

        # Display the user message immediately
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                # Get the actual response from modular orchestrator
                response = st.session_state.runner.process_query(user_input)

                # Create and display AI message
                ai_message = AIMessage(content=response)
                st.session_state.messages.append({"message": ai_message})

                # Display response
                st.write(response)

        # Rerun to update chat history
        st.rerun()


def multi_agent_app():
    """Main function for the Modular Multi-Agent Streamlit app."""
    user_input = orchestrate_streamlit_and_get_user_input(
        "Multi Agent System",
        "Should we switch from supplier SUP001 to SUP002 for our semiconductor components?",
        "Check compliance status for supplier SUP001"
    )
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = ModularMultiAgentOrchestrator(callbacks=[GalileoCallback()])

    # Process user input
    if user_input:
        # Add user message to chat history
        user_message = HumanMessage(content=user_input)
        st.session_state.messages.append({
            "message": user_message,
            "agent": "user"
        })

        # Display the user message immediately
        with st.chat_message("user"):
            st.write(user_input)

        # Get routing decision and display workflow info
        routing_decision = st.session_state.orchestrator.get_routing_decision(user_input)
        # Get response from modular orchestrator
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):

                # Get the actual response from modular orchestrator
                response = st.session_state.orchestrator.process_query(user_input)

                # Create and display AI message
                ai_message = AIMessage(content=response)
                agent_type = "synthesized" if routing_decision.get("requires_collaboration") else "single_agent"
                st.session_state.messages.append({
                    "message": ai_message,
                    "agent": agent_type
                })

                # Display response
                st.write(response)

        # Rerun to update chat history
        st.rerun()


def financial_agent_app():
    user_input = orchestrate_streamlit_and_get_user_input(
        "Financial Agent",
        "What are the financial risks of using supplier SUP001 vs SUP002 in SouthEast Asia?",
        "When comparing supplier SUP001 vs SUP002, how should I factor in the Total Cost of Ownership?"
    )
    if "runner" not in st.session_state:
        st.session_state.runner = FinancialAgentRunner(callbacks=[GalileoCallback()])
    process_input_for_simple_app(user_input)


def supply_chain_agent_app():
    user_input = orchestrate_streamlit_and_get_user_input(
        "Supply Chain Agent",
        "Check compliance status for supplier SUP001",
        "What are the fundamentals of Supply Chain Management?"
    )
    if "runner" not in st.session_state:
        st.session_state.runner = SupplyChainAgentRunner(callbacks=[GalileoCallback()])
    process_input_for_simple_app(user_input)


if __name__ == "__main__":
    os.environ["GALILEO_PROJECT"] = "sid-visa-playground"

    # os.environ["GALILEO_LOG_STREAM"] = "supply-chain"
    # supply_chain_agent_app()

    # os.environ["GALILEO_LOG_STREAM"] = "financial-agent"
    # financial_agent_app()

    os.environ["GALILEO_LOG_STREAM"] = "multi-agent"
    multi_agent_app()
