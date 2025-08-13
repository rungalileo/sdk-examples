import json
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from supply_chain_agent import get_supply_chain_agent
from financial_agent import get_financial_agent
from shared_state import State
from translators import multilingual_combination, hindi_translation, spanish_translation


def intent_classifier(state: State):
    """
    Classify the user's intent and route to appropriate agent(s)
    Similar to the intent_classifier in the example
    """
    # Get the latest user message
    user_query = ""
    for message in reversed(state["messages"]):
        if hasattr(message, 'content') and message.content:
            user_query = message.content
            break

    if not user_query:
        return {"next_agent": "supply_chain_agent"}

    # Use LLM to classify intent
    classifier_llm = ChatOpenAI(model="gpt-4", temperature=0, name="Classifier LLM")

    classification_prompt = f"""
    Analyze this user query and classify which agent(s) should handle it.

    User Query: "{user_query}"

    Available Agents:
    - supply_chain_agent: Handles supply chain management, risk assessment, supplier compliance, logistics, operational analysis. This agent can answer questions about everything that impacts supply chains including but not limited to weather and news.
    - financial_agent: Handles cost analysis, financial risk, ROI calculations, budget planning, TCO analysis
    - both_agents: Requires collaboration between both agents

    Examples:
    - "Check supplier compliance" → supply_chain_agent
    - "Calculate TCO" → financial_agent  
    - "Should we switch suppliers?" → both_agents
    
    If the query does not fit into any of three agents, respond with supply_chain_agent by default.
    
    Respond with ONLY a JSON object:
    {{
        "primary_agent": "supply_chain_agent" | "financial_agent" | "both_agents",
        "reasoning": "brief explanation of routing decision"
    }}
    """

    response = classifier_llm.invoke([HumanMessage(content=classification_prompt)])

    try:
        classification = json.loads(response.content)
        next_agent = classification.get("primary_agent", "supply_chain_agent")
    except:
        # Fallback to supply chain agent
        next_agent = "supply_chain_agent"

    # Store the routing decision in state (we'll add this to State)
    return {"next_agent": next_agent}


def route_to_agents(state: State):
    """
    Determine which path to take based on classification
    """
    next_agent = state.get("next_agent", "supply_chain_agent")

    if next_agent == "both_agents":
        return "supply_chain_agent"  # Start with supply chain, then go to financial
    else:
        return next_agent


# Global variable to store callbacks for subgraphs
_subgraph_callbacks = None


def set_subgraph_callbacks(callbacks):
    """Set callbacks that will be used by subgraphs"""
    global _subgraph_callbacks
    _subgraph_callbacks = callbacks


def financial_with_context(state: State):
    """
    Wrapper for financial agent that adds context from supply chain agent
    when running in collaborative mode
    """
    # Check if we have supply chain results to add as context
    supply_chain_result = None
    for message in reversed(state["messages"]):
        if hasattr(message, 'content') and "supply chain" in message.content.lower():
            supply_chain_result = message.content
            break

    config = {"configurable": {"thread_id": "financial-subgraph"}}
    if _subgraph_callbacks:
        config["callbacks"] = _subgraph_callbacks
    financial_agent = get_financial_agent()

    if supply_chain_result and state.get("next_agent") == "both_agents":
        # Add context message for financial agent
        context_message = SystemMessage(content=f"""
        Context from Supply Chain Analysis:
        {supply_chain_result}

        Please provide financial analysis that complements the supply chain analysis above.
        Focus on cost implications, ROI calculations, and financial risks related to the supply chain recommendations.
        Consider the operational factors mentioned in the supply chain analysis.
        """)

        # Add context to messages
        messages_with_context = state["messages"] + [context_message]
        modified_state = {**state, "messages": messages_with_context}

        return financial_agent.invoke(modified_state, config)
    else:
        return financial_agent.invoke(state, config)


def synthesize_followup(state: State):
    """
    Synthesize results from both agents when collaboration is needed
    Similar to compile_followup in the example
    """
    if state.get("next_agent") != "both_agents":
        # No synthesis needed for single agent
        return {}

    # Get the original user query
    user_query = ""
    for message in state["messages"]:
        if hasattr(message, 'content') and not hasattr(message, 'tool_calls'):
            user_query = message.content
            break

    # Extract the results from both agents
    supply_chain_result = ""
    financial_result = ""

    # Find the last few AI messages (results from agents)
    ai_messages = [msg for msg in state["messages"] if hasattr(msg, 'content') and hasattr(msg, 'response_metadata')]

    if len(ai_messages) >= 2:
        supply_chain_result = ai_messages[-2].content
        financial_result = ai_messages[-1].content

    # Synthesize the results
    synthesis_llm = ChatOpenAI(model="gpt-4", temperature=0, name="Synthesis LLM")

    synthesis_prompt = f"""
    Synthesize a comprehensive response by combining insights from both specialized agents.

    Original User Query: "{user_query}"

    SUPPLY CHAIN AGENT ANALYSIS:
    {supply_chain_result}

    FINANCIAL AGENT ANALYSIS:
    {financial_result}

    Please provide a unified response that:
    1. Directly answers the user's original query
    2. Integrates insights from both agents seamlessly
    3. Highlights any trade-offs between operational and financial considerations
    4. Provides clear, actionable recommendations
    5. Is well-structured and easy to understand

    Do not simply concatenate the responses - create a cohesive synthesis that balances both perspectives.
    """

    synthesis_response = synthesis_llm.invoke([HumanMessage(content=synthesis_prompt)])

    return {"messages": [synthesis_response]}


def supply_chain_with_callbacks(state: State):
    """
    Wrapper for supply chain agent to ensure callbacks are passed through
    """
    supply_chain_agent = get_supply_chain_agent()
    config = {"configurable": {"thread_id": "supply-chain-subgraph"}}

    if _subgraph_callbacks:
        config["callbacks"] = _subgraph_callbacks

    return supply_chain_agent.invoke(state, config)


def get_modular_multi_agent():
    """
    Create the main orchestrator graph using existing agent subgraphs as nodes
    """
    # Build the main orchestrator graph
    graph_builder = StateGraph(State)

    # Add the intent classifier
    graph_builder.add_node("intent_classifier", intent_classifier)

    # Add the compiled subgraphs as nodes with callback wrappers
    graph_builder.add_node("supply_chain_agent", supply_chain_with_callbacks)
    graph_builder.add_node("financial_agent", financial_with_context)

    # Add synthesis node
    graph_builder.add_node("synthesize_followup", synthesize_followup)

    # Add translation nodes
    graph_builder.add_node("spanish_translation", spanish_translation)
    graph_builder.add_node("hindi_translation", hindi_translation)

    # Add final combination node
    graph_builder.add_node("multilingual_combination", multilingual_combination)

    # Set entry point
    graph_builder.add_edge(START, "intent_classifier")

    # Add conditional routing from intent classifier
    graph_builder.add_conditional_edges(
        "intent_classifier",
        route_to_agents,
        {
            "supply_chain_agent": "supply_chain_agent",
            "financial_agent": "financial_agent",
            "both_agents": "supply_chain_agent"  # Start with supply chain for collaboration
        }
    )

    # For collaborative workflows: supply_chain -> financial -> synthesis
    def after_supply_chain(state: State):
        if state.get("next_agent") == "both_agents":
            return "financial_agent"
        else:
            return "synthesize_followup"

    graph_builder.add_conditional_edges(
        "supply_chain_agent",
        after_supply_chain,
        {
            "financial_agent": "financial_agent",
            "synthesize_followup": "synthesize_followup"
        }
    )

    # Financial agent always goes to synthesis
    graph_builder.add_edge("financial_agent", "synthesize_followup")

    graph_builder.add_edge("synthesize_followup", "spanish_translation")
    graph_builder.add_edge("synthesize_followup", "hindi_translation")

    # Both translation nodes go to final combination
    graph_builder.add_edge("spanish_translation", "multilingual_combination")
    graph_builder.add_edge("hindi_translation", "multilingual_combination")

    # Final combination goes to end
    graph_builder.add_edge("multilingual_combination", END)

    return graph_builder.compile()


class ModularMultiAgentOrchestrator:
    """
    Orchestrator that uses existing agent subgraphs as building blocks
    """

    def __init__(self, callbacks=None):
        set_subgraph_callbacks(callbacks)
        self.graph = get_modular_multi_agent()
        self.config = {"configurable": {"thread_id": "modular-multi-agent"}}

        if callbacks:
            self.config["callbacks"] = callbacks

    def process_query(self, user_query: str) -> str:
        """Process a query through the modular multi-agent system"""
        initial_state = {"messages": [HumanMessage(content=user_query)]}
        result = self.graph.invoke(initial_state, self.config)

        # Return the last message content
        if result["messages"]:
            return result["messages"][-1].content
        return "No response generated"

    def get_routing_decision(self, user_query: str) -> Dict[str, Any]:
        """Get routing decision without full execution"""
        # Just run the intent classifier
        state = {"messages": [HumanMessage(content=user_query)]}
        classifier_result = intent_classifier(state)

        next_agent = classifier_result.get("next_agent", "supply_chain_agent")

        return {
            "primary_agent": next_agent,
            "requires_collaboration": next_agent == "both_agents",
            "execution_order": ["supply_chain", "financial"] if next_agent == "both_agents" else [
                next_agent.replace("_agent", "")]
        }
