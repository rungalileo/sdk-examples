from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage

from rag_tool import rag_search
from shared_state import State
from tools import check_supplier_compliance, assess_disruption_risk

load_dotenv()

TOOLS = [TavilySearch(max_results=2), assess_disruption_risk, check_supplier_compliance, rag_search]
llm_with_tools = ChatOpenAI(model="gpt-4", name="Supply Chain Agent").bind_tools(TOOLS)


def invoke_chatbot(state):
    """Create an LLM with the specified tools."""
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


def get_supply_chain_agent() -> CompiledStateGraph:
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


class SupplyChainAgentRunner:
    def __init__(self, callbacks=None):
        self.graph = get_supply_chain_agent()
        self.config = {"configurable": {"thread_id": "supply-chain-agent"}}

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
