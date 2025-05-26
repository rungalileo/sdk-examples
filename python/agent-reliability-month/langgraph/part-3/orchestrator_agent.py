from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from financial_agent import get_financial_agent  # The agent we just created
from supply_chain_agent import get_supply_chain_agent


class MultiAgentOrchestrator:
    """
    Orchestrates communication between multiple specialized agents
    """

    def __init__(self):
        self.agents = {
            "supply_chain": get_supply_chain_agent(),
            "financial": get_financial_agent()
        }
        self.routing_llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.config = {"configurable": {"thread_id": "multi-agent"}}

    def route_query(self, user_query: str) -> Dict[str, Any]:
        """
        Determine which agent(s) should handle the query and in what order
        """
        routing_prompt = f"""
        Analyze this user query and determine which agents should handle it:

        User Query: "{user_query}"

        Available Agents:
        - supply_chain: Handles supply chain management, risk assessment, supplier compliance, logistics
        - financial: Handles cost analysis, financial risk, ROI calculations, budget planning

        Respond with a JSON object containing:
        - primary_agent: The main agent to handle the query
        - secondary_agents: List of other agents that might need to contribute
        - requires_collaboration: Boolean indicating if agents need to work together
        - execution_order: List of agents in order of execution

        Example response:
        {{
            "primary_agent": "supply_chain",
            "secondary_agents": ["financial"],
            "requires_collaboration": true,
            "execution_order": ["supply_chain", "financial"]
        }}
        """

        response = self.routing_llm.invoke([HumanMessage(content=routing_prompt)])

        # Parse the response (in production, you'd want better error handling)
        try:
            import json
            routing_decision = json.loads(response.content)
            return routing_decision
        except:
            # Fallback to supply_chain agent if routing fails
            return {
                "primary_agent": "supply_chain",
                "secondary_agents": [],
                "requires_collaboration": False,
                "execution_order": ["supply_chain"]
            }

    def execute_collaborative_workflow(self, user_query: str, routing_decision: Dict) -> str:
        """
        Execute a workflow that requires multiple agents to collaborate
        """
        results = {}
        conversation_history = [HumanMessage(content=user_query)]

        for agent_name in routing_decision["execution_order"]:
            agent = self.agents[agent_name]

            # Add context from previous agents if this isn't the first
            if len(results) > 0:
                context_message = self._build_context_message(results, agent_name)
                agent_messages = conversation_history + [context_message]
            else:
                agent_messages = conversation_history

            # Execute the agent
            result = agent.invoke({"messages": agent_messages}, self.config)
            latest_message = result["messages"][-1]
            results[agent_name] = latest_message.content

            # Add the result to conversation history for next agent
            conversation_history.append(latest_message)

        # Synthesize final response
        return self._synthesize_final_response(user_query, results, routing_decision)

    def _build_context_message(self, previous_results: Dict, current_agent: str) -> SystemMessage:
        """
        Build context message for current agent based on previous agents' results
        """
        context = f"Context from other agents:\n\n"
        for agent_name, result in previous_results.items():
            context += f"Results from {agent_name} agent:\n{result}\n\n"

        if current_agent == "financial":
            context += """
            Please provide financial analysis that complements the supply chain analysis above.
            Focus on cost implications, ROI calculations, and financial risks related to the supply chain recommendations.
            """
        elif current_agent == "supply_chain":
            context += """
            Please consider the financial analysis above when providing supply chain recommendations.
            Balance operational efficiency with cost considerations.
            """

        return SystemMessage(content=context)

    def _synthesize_final_response(self, user_query: str, results: Dict, routing_decision: Dict) -> str:
        """
        Synthesize a final response that combines insights from multiple agents
        """
        if not routing_decision["requires_collaboration"]:
            # Single agent response
            primary_agent = routing_decision["primary_agent"]
            return results[primary_agent]

        # Multi-agent synthesis
        synthesis_prompt = f"""
        Synthesize a comprehensive response to the user's query by combining insights from multiple specialized agents.

        Original Query: "{user_query}"

        Agent Responses:
        """

        for agent_name, result in results.items():
            synthesis_prompt += f"\n{agent_name.upper()} AGENT RESPONSE:\n{result}\n"

        synthesis_prompt += """

        Please provide a unified response that:
        1. Directly answers the user's query
        2. Integrates insights from all agents
        3. Highlights any trade-offs or considerations between different perspectives
        4. Provides actionable recommendations
        5. Is clear and well-structured

        Do not simply concatenate the responses - synthesize them into a cohesive answer.
        """

        synthesis_response = self.routing_llm.invoke([HumanMessage(content=synthesis_prompt)])
        return synthesis_response.content

    def process_query(self, user_query: str) -> str:
        """
        Main method to process a user query through the multi-agent system
        """
        # Route the query
        routing_decision = self.route_query(user_query)

        # Execute based on routing decision
        if routing_decision["requires_collaboration"]:
            return self.execute_collaborative_workflow(user_query, routing_decision)
        else:
            # Single agent execution
            primary_agent = routing_decision["primary_agent"]
            agent = self.agents[primary_agent]
            result = agent.invoke({"messages": [HumanMessage(content=user_query)]}, self.config)
            return result["messages"][-1].content


# Example usage workflows
EXAMPLE_WORKFLOWS = {
    "supplier_evaluation": {
        "query": "Should we switch from supplier SUP001 to SUP002 for our semiconductor components?",
        "expected_flow": [
            "1. Supply Chain Agent: Assess compliance, risk, and operational factors",
            "2. Financial Agent: Calculate TCO and financial impact of switch",
            "3. Synthesis: Provide recommendation balancing operational and financial factors"
        ]
    },
    "risk_mitigation": {
        "query": "What's the financial impact of implementing backup suppliers in Southeast Asia?",
        "expected_flow": [
            "1. Supply Chain Agent: Assess risks in Southeast Asia and mitigation strategies",
            "2. Financial Agent: Calculate costs of backup suppliers and risk mitigation",
            "3. Synthesis: Cost-benefit analysis of risk mitigation strategies"
        ]
    },
    "inventory_optimization": {
        "query": "How should we adjust our inventory levels to balance costs and supply risk?",
        "expected_flow": [
            "1. Supply Chain Agent: Analyze supply risks and optimal inventory strategies",
            "2. Financial Agent: Calculate working capital impact and carrying costs",
            "3. Synthesis: Optimal inventory strategy balancing risk and cost"
        ]
    }
}
