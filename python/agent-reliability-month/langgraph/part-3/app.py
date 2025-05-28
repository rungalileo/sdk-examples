import os
import time

import streamlit as st
from galileo import galileo_context
from galileo.handlers.langchain import GalileoCallback
from langchain_core.messages import AIMessage, HumanMessage

from orchestrator import ModularMultiAgentOrchestrator


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


def display_system_architecture():
    """Display the modular system architecture"""
    with st.sidebar:
        st.header("🏗️ Modular Architecture")

        # System Overview
        with st.expander("📋 System Components", expanded=True):
            st.markdown("""
            **Main Orchestrator Graph:**
            - `intent_classifier` → Routes queries
            - `supply_chain_agent` → Compiled subgraph
            - `financial_agent` → Compiled subgraph  
            - `synthesis_followup` → Combines results
            """)

        # Supply Chain Subgraph
        with st.expander("📦 Supply Chain Subgraph"):
            st.markdown("""
            **Independent LangGraph:**
            - Risk assessment tools
            - Compliance checking
            - RAG knowledge base
            - Web search capabilities
            """)

        # Financial Subgraph
        with st.expander("💰 Financial Subgraph"):
            st.markdown("""
            **Independent LangGraph:**
            - TCO calculations
            - Financial risk analysis
            - Cost comparisons
            - ROI analysis
            """)

        st.header("🔄 Workflow Types")
        st.markdown("""
        **Single Agent Workflows:**
        ```
        intent_classifier → agent → synthesis
        ```

        **Collaborative Workflows:**
        ```
        intent_classifier → supply_chain → financial → synthesis
        ```
        """)


def show_example_queries():
    """Show example queries demonstrating the modular system"""
    st.header("💡 Try These Modular Examples")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔄 Multi-Agent Collaboration")
        if st.button("Should we switch suppliers?", key="supplier_decision"):
            return "Should we switch from supplier SUP001 to SUP002 for our semiconductor components? Consider both operational and financial factors."

        if st.button("Cost-benefit of risk mitigation?", key="risk_cost"):
            return "What's the cost-benefit analysis of implementing backup suppliers in Southeast Asia to mitigate supply chain risks?"

    with col2:
        st.subheader("🎯 Single Agent Routing")
        if st.button("Check SUP001 compliance", key="compliance_single"):
            return "Check the compliance status for supplier SUP001"

        if st.button("Calculate TCO for SUP002", key="tco_single"):
            return "Calculate the total cost of ownership for supplier SUP002 with annual volume of 50000 units at $15 per unit"

    # Additional examples in full width
    col3, col4 = st.columns(2)

    with col3:
        if st.button("Risk assessment - Southeast Asia", key="risk_assessment"):
            return "What's the supply chain risk in Southeast Asia right now?"

    with col4:
        if st.button("Financial risk analysis", key="financial_risk"):
            return "Analyze the financial risk for supplier SUP001"

    return None


def display_workflow_info(routing_decision):
    """Display information about the workflow being executed"""
    if routing_decision.get("requires_collaboration", False):
        st.info(f"""
        🔄 **Multi-Agent Collaborative Workflow**

        **Flow:** Intent Classifier → {' → '.join(routing_decision['execution_order'])} → Synthesis

        Each agent runs as an independent compiled subgraph within the main orchestrator.
        """)
    else:
        agent_name = routing_decision.get("primary_agent", "unknown").replace("_agent", "")
        st.info(f"""
        🎯 **Single Agent Workflow**

        **Flow:** Intent Classifier → {agent_name.title()} Agent → Synthesis

        Direct routing to specialized subgraph.
        """)


def main(session_name="Modular Multi-Agent Demo"):
    """Main function for the Modular Multi-Agent Streamlit app."""

    # Configure page
    st.set_page_config(
        page_title="Modular Multi-Agent Supply Chain System",
        page_icon="🧩",
        layout="wide"
    )

    # App title and description
    st.title("🧩 Modular Multi-Agent Supply Chain System")
    st.markdown("""
    This system demonstrates **modular agent composition** where existing compiled agent subgraphs 
    are used as nodes in a higher-level orchestrator graph. Each agent maintains its independence 
    while being coordinated by the main workflow.
    """)

    # Display system architecture
    display_system_architecture()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "orchestrator_initialized" not in st.session_state:
        st.session_state.orchestrator_initialized = False

    # Initialize the modular orchestrator
    if not st.session_state.orchestrator_initialized:
        # Start Galileo session BEFORE initializing orchestrator
        try:
            galileo_context.start_session(name=session_name)
            st.session_state.orchestrator = initialize_modular_orchestrator()
            st.session_state.orchestrator_initialized = True
        except Exception as e:
            st.error(f"Failed to start Galileo session: {str(e)}")
            st.stop()

        # Add welcome message
        welcome_message = AIMessage(content="""
        Welcome to the Modular Multi-Agent Supply Chain System! 🧩

        **Architecture Highlights:**
        - **Modular Design**: Each agent is an independent compiled subgraph
        - **Intelligent Routing**: Intent classifier routes queries to appropriate agents  
        - **Flexible Composition**: Subgraphs are composed as nodes in the main orchestrator
        - **Context Sharing**: Agents collaborate when needed while maintaining independence

        **Available Agents:**
        - 📦 **Supply Chain Agent**: Risk assessment, compliance, operational analysis
        - 💰 **Financial Agent**: Cost analysis, TCO calculations, financial risk assessment

        Ask me anything, and I'll automatically route to the right agent(s)!
        """)
        st.session_state.messages.append({
            "message": welcome_message,
            "agent": "system"
        })

    # Show example queries
    example_query = show_example_queries()

    # Display chat history
    display_chat_history()

    # Get user input
    user_input = st.chat_input("Ask about supply chain strategy, costs, risks, or supplier decisions...")

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

    # Add footer with system information
    with st.sidebar:
        st.markdown("---")
        st.caption("🔧 **System Status**")
        if st.session_state.orchestrator_initialized:
            st.success("✅ Modular Orchestrator: Ready")
            st.success("✅ Supply Chain Subgraph: Loaded")
            st.success("✅ Financial Subgraph: Loaded")
            st.success("✅ Intent Classifier: Active")
        else:
            st.warning("⏳ System: Initializing...")

        st.markdown("---")
        st.caption("🧩 **Modular Architecture**")
        st.code("""
        Main Orchestrator Graph:
        ├── intent_classifier
        ├── supply_chain_agent (subgraph)
        ├── financial_agent (subgraph)  
        └── synthesis_followup
        """)

        st.markdown("---")
        st.caption("📊 **Benefits**")
        st.markdown("""
        - **Independent Development**: Agents can be developed separately
        - **Reusable Components**: Subgraphs can be used in other contexts
        - **Clean Composition**: Clear separation of concerns
        - **Easy Testing**: Each subgraph can be tested independently
        """)


if __name__ == "__main__":
    os.environ["GALILEO_PROJECT"] = "sid-multi-agent-v1" # "modular-multi-agent-supply-chain"
    os.environ["GALILEO_LOG_STREAM"] = "dev"
    main(session_name=f"Modular Multi-Agent Demo - {int(time.time())}")
