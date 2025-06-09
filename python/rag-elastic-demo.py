# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "elasticsearch",
#   "langchain-elasticsearch",
#   "langchain-openai",
#   "langgraph",
#   "galileo",
#   "openai",
# ]
# ///

# # --- Required Environment Variables ---
# 
# # Elasticsearch connection & indexes
# ES_HOST="COPY FROM CLOUD.ELASTIC.CO"
# ES_API_KEY="COPY FROM CLOUD.ELASTIC.CO"
# ES_INDEX="demo"
# ES_INDEX_CHAT_HISTORY="demo-chat-history"
# ELSER_MODEL=".elser_model_2_linux-x86_64"
# 
# # External service API keys
# OPENAI_API_KEY="YOUR OPENAI KEY"
# GALILEO_API_KEY="YOUR GALILEO OPENAI KEY"
# 
# # Galileo observability settings
# GALILEO_PROJECT="elastic"
# GALILEO_LOG_STREAM="my_log_stream"

import os
import time
from typing import Annotated, Sequence

from elasticsearch import Elasticsearch, NotFoundError
from langchain.tools.retriever import create_retriever_tool
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.documents import Document
from langchain_elasticsearch import ElasticsearchStore, SparseVectorStrategy
from langchain_elasticsearch import ElasticsearchChatMessageHistory
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

# --- 1. Configuration ---
# Set up your connection details and index names.
# It's recommended to use environment variables for sensitive data.
ES_HOST = os.getenv("ES_HOST")
ES_API_KEY = os.getenv("ES_API_KEY")
ES_INDEX = os.getenv("ES_INDEX", "demo")
ES_INDEX_CHAT_HISTORY = os.getenv("ES_INDEX_CHAT_HISTORY", "chat-history")
ELSER_MODEL = os.getenv("ELSER_MODEL", ".elser_model_2_linux-x86_64")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Ensure your OpenAI key is set

# --- 2. Elasticsearch Setup ---
# Connect to Elasticsearch ensure your IP is unblocked
print("Connecting to Elasticsearch...")
elasticsearch_client = Elasticsearch(hosts=[ES_HOST], api_key=ES_API_KEY)
print(elasticsearch_client.info())

def setup_elasticsearch():
    """
    Ensures the ELSER model is deployed and sample documents are indexed.
    """
    # 2a. Deploy ELSER Model (Elastic's NLP model for semantic search)
    try:
        elasticsearch_client.ml.get_trained_models(model_id=ELSER_MODEL)
        print(f'ELSER model "{ELSER_MODEL}" is already available.')
    except NotFoundError:
        print(f'ELSER model "{ELSER_MODEL}" not found, starting deployment...')
        elasticsearch_client.ml.put_trained_model(
            model_id=ELSER_MODEL, input={"field_names": ["text_field"]}
        )
        while True:
            status = elasticsearch_client.ml.get_trained_models(model_id=ELSER_MODEL, include="definition_status")
            if status["trained_model_configs"][0]["fully_defined"]:
                break
            time.sleep(1)
        elasticsearch_client.ml.start_trained_model_deployment(
            model_id=ELSER_MODEL, wait_for="fully_allocated"
        )
        print(f'ELSER model "{ELSER_MODEL}" deployed successfully.')

    store = ElasticsearchStore(
        es_connection=elasticsearch_client,
        index_name=ES_INDEX,
        strategy=SparseVectorStrategy(model_id=ELSER_MODEL),
    )
    sample_docs = [
        Document(page_content="Our company offers comprehensive health insurance including medical, dental, and vision coverage.", metadata={"source": "employee_handbook"}),
        Document(page_content="Remote work policy allows employees to work from home up to 3 days per week.", metadata={"source": "employee_handbook"}),
        Document(page_content="The company's vacation policy provides 15 days of paid time off for new employees, increasing to 20 days after 3 years of service.", metadata={"source": "employee_handbook"}),
    ]
    store.add_documents(sample_docs)
    time.sleep(2) # Give time for indexing
    print(f"{len(sample_docs)} documents indexed successfully.")
    return store

# --- 3. Agent Definition ---
# Define the state, tools, and the graph that powers the agent.

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# The retriever tool searches Elasticsearch for relevant documents.
def setup_agent_and_graph(store: ElasticsearchStore):
    """
    Sets up the agent, tools, and the LangGraph workflow.
    """
    retriever = store.as_retriever()
    retriever_tool = create_retriever_tool(
        retriever,
        "retrieve_workplace_documents",
        "Search and return information about company policies, benefits, and processes.",
    )
    tools = [retriever_tool]

    # Use a model that is good at tool use
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True, api_key=OPENAI_API_KEY)
    agent_runnable = llm.bind_tools(tools)

    # 3c. Define the Graph
    # The graph defines the flow of control for the agent.
    def run_agent(state: AgentState):
        """Invokes the agent to decide on the next action."""
        return {"messages": [agent_runnable.invoke(state["messages"])]}

    tool_node = ToolNode(tools)
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", run_agent)
    workflow.add_node("tools", tool_node)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    graph = workflow.compile()
    return graph

# --- 4. Run the Agent ---
# Now, we can ask questions and get answers.
def ask_question(graph, question: str, session_id: str):
    """
    Asks a question to the RAG agent and returns the answer.
    """
    chat_history = ElasticsearchChatMessageHistory(
        es_connection=elasticsearch_client,
        index=ES_INDEX_CHAT_HISTORY,
        session_id=session_id
    )

    inputs = {"messages": [HumanMessage(content=question)]}
    final_state = graph.invoke(inputs, config={"recursion_limit": 5})
    response = final_state["messages"][-1].content

    # Save conversation history
    chat_history.add_user_message(question)
    chat_history.add_ai_message(response)
    return response

# Step 1: Set up Elasticsearch index and data
document_store = setup_elasticsearch()

# Step 2: Compile the agent and its workflow
rag_agent_graph = setup_agent_and_graph(document_store)

# Step 3: Start a Q&A session
print("\n--- Starting Q&A Session ---")
session_id = f"session-{int(time.time())}"

# Ask the first question
question1 = "How many vacation days do new hires get?"
print(f"\n❓ Question: {question1}")
answer1 = ask_question(rag_agent_graph, question1, session_id)
print(f"✅ Answer: {answer1}")

# Ask a follow-up question
question2 = "What about health insurance?"
print(f"\n❓ Question: {question2}")
answer2 = ask_question(rag_agent_graph, question2, session_id)
print(f"✅ Answer: {answer2}")
