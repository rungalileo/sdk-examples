"""
Builds a graph using all the nodes and edges defined in the application.
"""

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
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

    # Initialize the memory saver to store the state of messages in the graph.
    # This allows us to have a conversation history using the ChainLit session ID
    memory = MemorySaver()

    # Create an agent
    agent = create_react_agent(
        model=ChatOpenAI(model="gpt-4.1-mini", name="Credit Card Agent"),
        tools=[credit_card_information_retrieval_tool],
        prompt=(
            """
            You are an agent providing help on the credit card options at Brahe Bank.
            Be helpful, but succinct, and do not make up information that you do not already know to be true.
            If you need to retrieve information from the knowledge base, use the tools provided.
            If you are asked questions about credit card options, you can use the information you have to help the user. For example, you can answer questions about which
            card may best align with their interests if their interests align with rewards or features of a card.
            If you do not know the answer to a question, you can say that you do not know.
            """
        ),
        name="credit-card-agent",
        checkpointer=memory,
    )

    # Uncomment the following lines to print the compiled graph to the console in Mermaid format
    # print("Compiled Credit Card Agent Graph:")
    # print(agent.get_graph().draw_mermaid())

    # Return the compiled graph
    return agent
