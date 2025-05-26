from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from financial_agent_tools import calculate_tco, analyze_financial_risk, compare_supplier_costs
from shared_state import State

FINANCIAL_TOOLS = [calculate_tco, analyze_financial_risk, compare_supplier_costs]


def get_financial_agent():
    """Create the financial analysis agent"""
    llm_with_financial_tools = ChatOpenAI(model="gpt-4").bind_tools(FINANCIAL_TOOLS)

    def invoke_financial_chatbot(state):
        message = llm_with_financial_tools.invoke(state["messages"])
        return {"messages": [message]}

    # Build the graph (similar structure to supply chain agent)
    graph_builder = StateGraph(State)  # Assuming State is imported
    graph_builder.add_node("financial_chatbot", invoke_financial_chatbot)

    tool_node = ToolNode(tools=FINANCIAL_TOOLS)
    graph_builder.add_node("financial_tools", tool_node)

    graph_builder.add_conditional_edges("financial_chatbot", tools_condition)
    graph_builder.add_edge("financial_tools", "financial_chatbot")
    graph_builder.add_edge("START", "financial_chatbot")

    return graph_builder.compile()
