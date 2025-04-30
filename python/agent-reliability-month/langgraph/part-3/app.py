import os
import time
import uuid

import streamlit as st
from dotenv import load_dotenv
from galileo import galileo_context
from galileo.handlers.langchain import GalileoCallback
from langchain_core.messages import AIMessage, HumanMessage

from orchestrator import ModularMultiAgentOrchestrator

load_dotenv()

def display_chat_history():
    """Display all messages in the chat history with agent attribution."""
    if not st.session_state.messages:
        return

    for message_data in st.session_state.messages:
        if isinstance(message_data, dict):
            message = message_data.get("message")
            agent = message_data.get("agent", "user")

            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    if agent != "system" and agent != "synthesized":
                        st.caption(f"🤖 {agent.title()} Response")
                    st.write(message.content)
        else:
            # Fallback for old message format
            if isinstance(message_data, HumanMessage):
                with st.chat_message("user"):
                    st.write(message_data.content)
            elif isinstance(message_data, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message_data.content)


def initialize_modular_orchestrator():
    """Initialize the modular multi-agent orchestrator"""
    with st.spinner("Initializing Modular Multi-Agent System..."):
        try:
            # Initialize Galileo callback with proper configuration
            galileo_callback = GalileoCallback()
            return ModularMultiAgentOrchestrator(callbacks=[galileo_callback])
        except Exception as e:
            st.error(f"Failed to initialize modular orchestrator: {str(e)}")
            st.stop()


def show_example_queries():
    """Show example queries demonstrating the modular system"""
    st.subheader("Example queries")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Multi-Agent")
        if st.button("Should we switch from supplier SUP001 to SUP002 for our semiconductor components?", key="supplier_decision"):
            return "Should we switch from supplier SUP001 to SUP002 for our semiconductor components?"

    with col2:
        st.subheader("Single Agent")
        if st.button("Check SUP001 compliance", key="compliance_single"):
            return "Check compliance status for supplier SUP001"
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


def main():
    """Main function for the Modular Multi-Agent Streamlit app."""

    # Configure page
    st.set_page_config(
        page_title="Modular Multi-Agent Supply Chain System",
        page_icon="🧩",
        layout="wide"
    )

    # App title and description
    st.title("Supply Chain System")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "orchestrator_initialized" not in st.session_state:
        st.session_state.orchestrator_initialized = False

    # Initialize the modular orchestrator
    if not st.session_state.orchestrator_initialized:
        # Start Galileo session BEFORE initializing orchestrator
        try:
            galileo_context.start_session(external_id=str(uuid.uuid4())[:10])
            st.session_state.orchestrator = initialize_modular_orchestrator()
            st.session_state.orchestrator_initialized = True
        except Exception as e:
            st.error(f"Failed to start Galileo session: {str(e)}")
            st.stop()

        # Add welcome message
        welcome_message = AIMessage(content="Welcome to the Supply Chain Agent! ")
        st.session_state.messages.append({
            "message": welcome_message,
            "agent": "system"
        })

    # Show example queries
    example_query = show_example_queries()

    # Display chat history
    display_chat_history()

    # Get user input
    user_input = st.chat_input("How can I help you?...")

    # Use example query if button was clicked
    if example_query:
        user_input = example_query

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
        display_workflow_info(routing_decision)

        # Get response from modular orchestrator
        with st.chat_message("assistant"):
            with st.spinner("Processing through modular agent workflow..."):

                # Show progress for multi-agent workflows
                if routing_decision.get("requires_collaboration", False):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    steps = ["Intent Classification", "Supply Chain Analysis", "Financial Analysis", "Synthesis"]

                    for i, step in enumerate(steps):
                        progress = (i + 1) / len(steps)
                        progress_bar.progress(progress)
                        status_text.text(f"🧩 {step}...")
                        time.sleep(0.8)

                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()

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


if __name__ == "__main__":
    os.environ["GALILEO_PROJECT"] = "sid-multi-agent-v1"
    os.environ["GALILEO_LOG_STREAM"] = "dev-v6"
    main()

    # Example queries:
    # 1. Check compliance status for supplier SUP001
    # 2. Should we switch from supplier SUP001 to SUP002 for our semiconductor components?
    # 3. Assess disruption risk for semiconductors in Southeast Asia
