"""
Builds a graph using all the nodes and edges defined in the application.
"""

import os
from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent

from ..tools.pinecone_retrieval_tool import PineconeRetrievalTool

# Create the tools
credit_card_information_retrieval_tool = PineconeRetrievalTool("credit-card-information")


def create_credit_card_information_agent() -> CompiledGraph:
    """
    Create an agent that can help with inquires about the available credit card options from the Brahe Bank.

    returns: A compiled graph for this agent.
    """

    # Create an agent
    agent = create_react_agent(
        model=ChatOpenAI(model=os.environ["MODEL_NAME"], name="Credit Card Agent"),
        tools=[credit_card_information_retrieval_tool],
        prompt=("""
            You are an expert on Brahe Bank credit card products. Provide clear, accurate,
            and concise information. Only answer with known facts from provided documentation,
            and information about the requestor such as their credit score.
            If unsure, state "I don't know."
            """),
        name="credit-card-agent",
    )

    # Uncomment the following lines to print the compiled graph to the console in Mermaid format
    # print("Compiled Credit Card Agent Graph:")
    # print(agent.get_graph().draw_mermaid())

    # Return the compiled graph
    return agent
