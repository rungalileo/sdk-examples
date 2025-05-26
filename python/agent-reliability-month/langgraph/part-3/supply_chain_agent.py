from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from rag_tool import rag_search, initialize_supply_chain_rag
from shared_state import State
from tools import check_supplier_compliance, assess_disruption_risk

load_dotenv()

TOOLS = [TavilySearch(max_results=2), assess_disruption_risk, check_supplier_compliance, rag_search]
llm_with_tools = ChatOpenAI(model="gpt-4").bind_tools(TOOLS)


def invoke_chatbot(state):
    """Create an LLM with the specified tools."""
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


def get_supply_chain_agent() -> CompiledStateGraph:
    initialize_supply_chain_rag()
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
