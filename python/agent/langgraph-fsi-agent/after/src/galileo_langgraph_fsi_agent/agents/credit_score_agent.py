"""
A credit score agent for the Brahe Bank application.
"""

from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent

from ..tools.credit_score_tool import CreditScoreTool


# Create the tools
credit_score_tool = CreditScoreTool()


def create_credit_score_agent() -> CompiledGraph:
    """
    Create an agent that can help with inquires about your credit score.

    returns: A compiled graph for this agent.
    """

    # Create an agent
    agent = create_react_agent(
        model=ChatOpenAI(model="gpt-4.1-mini", name="Credit Score Agent"),
        tools=[credit_score_tool],
        prompt=(
            # """
            # You are an agent providing help on the credit card options at Brahe Bank.
            # Be helpful, but succinct, and do not make up information that you do not already know to be true.
            # If you need to retrieve information from the knowledge base, use the tools provided.
            # If you are asked questions about credit card options, you can use the information you have to help the user. For example, you can answer questions about which
            # card may best align with their interests if their interests align with rewards or features of a card.
            # If you do not know the answer to a question, you can say that you do not know.
            # """
            """
            You are an expert on credit score. Provide the user with accurate and concise information about credit scores from the credit_score_tool.
            """
        ),
        name="credit-score-agent"
    )

    # Uncomment the following lines to print the compiled graph to the console in Mermaid format
    # print("Compiled Credit Score Agent Graph:")
    # print(agent.get_graph().draw_mermaid())

    # Return the compiled graph
    return agent
