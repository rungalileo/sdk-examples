# %% [markdown]
# LangChain + LangGraph agent with OTEL tracing (Galileo) and tool calling

# %%
# Install dependencies
!pip -q install --upgrade \
  opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation \
  openinference-instrumentation-langchain \
  langchain langchain-community langchain-openai langgraph langchain-text-splitters \
  beautifulsoup4 tiktoken

# %%
# Environment and config (do not hardcode secrets)
import os
from getpass import getpass

# Set your OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass("Enter OPENAI_API_KEY: ")

# Optional: Galileo OTEL export settings
# Provide these via env vars to enable tracing export
# os.environ["GALILEO_API_KEY"] = getpass("Enter GALILEO_API_KEY (or leave blank to skip): ")
# os.environ["GALILEO_PROJECT"] = "your_project"
# os.environ["GALILEO_LOGSTREAM"] = "default"
# os.environ["GALILEO_OTEL_ENDPOINT"] = "https://app.galileo.ai/api/galileo/otel/traces"
# For local testing you can set: http://localhost:8000/api/galileo/otel/traces

galileo_api_key = os.getenv("GALILEO_API_KEY", "")
galileo_project = os.getenv("GALILEO_PROJECT", "")
galileo_logstream = os.getenv("GALILEO_LOGSTREAM", "")
otel_endpoint = os.getenv("GALILEO_OTEL_ENDPOINT", "https://app.galileo.ai/api/galileo/otel/traces")

if galileo_api_key and galileo_project and galileo_logstream:
    headers = {
        "Galileo-API-Key": galileo_api_key,
        "project": galileo_project,
        "logstream": galileo_logstream,
    }
    os.environ["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = ",".join([f"{k}={v}" for k, v in headers.items()])

print("Environment configured. Galileo tracing export is", "enabled" if os.getenv("OTEL_EXPORTER_OTLP_TRACES_HEADERS") else "disabled")

# %%
# OpenTelemetry + OpenInference instrumentation for LangChain
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry import trace as trace_api
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.langchain import LangChainInstrumentor

resource = Resource.create({"service.name": "langchain-galileo-notebook"})
tracer_provider = trace_sdk.TracerProvider(resource=resource)

# Export to Galileo if configured
if os.getenv("OTEL_EXPORTER_OTLP_TRACES_HEADERS"):
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otel_endpoint)))

# Also log spans to console for debugging
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

# Register the provider globally
trace_api.set_tracer_provider(tracer_provider)

# Instrument LangChain
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

print("LangChain OTEL tracing initialized.")

# %%
# Build a retrieval tool from Lilian Weng blog posts
from langgraph.prebuilt import create_react_agent
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")  # or "text-embedding-3-large"
embeddings = OpenAIEmbeddings(model=EMBED_MODEL)

urls = [
    "https://lilianweng.github.io/posts/2024-11-28-reward-hacking/",
    "https://lilianweng.github.io/posts/2024-07-07-hallucination/",
    "https://lilianweng.github.io/posts/2024-04-12-diffusion-video/",
]

# Load web pages
docs = []
for url in urls:
    try:
        docs.extend(WebBaseLoader(url).load())
    except Exception as e:
        print(f"Failed to load {url}: {e}")

# Split documents
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=100, chunk_overlap=50)
doc_splits = text_splitter.split_documents(docs)

# Create in-memory vector store and retriever
vectorstore = InMemoryVectorStore.from_documents(doc_splits, embedding=embeddings)
retriever = vectorstore.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    name="retrieve_blog_posts",
    description="Search and return information about Lilian Weng blog posts.",
)

len(doc_splits)

# %%
# Create a ReAct agent with tools
from langchain_core.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    print(f"Multiplying {a} and {b}")
    return a * b

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_react_agent(
    model="openai:gpt-4o-mini",
    tools=[get_weather, multiply, retriever_tool],
    prompt="You are a helpful assistant."
)

print("Agent created.")

# %%
# Run the agent (sample invocations)
def run_agent_message(message):
    result = agent.invoke({"messages": [message]})
    msgs = result.get("messages") or []
    final = msgs[-1].content if msgs else "(no output)"
    print(final)

print("Query 1:")
run_agent_message({"role": "user", "content": "what is the weather in sf"})

print("\nQuery 2:")
run_agent_message({"role": "user", "content": "what is 12 * 666 with the tool"})

print("\nQuery 3:")
run_agent_message({"role": "user", "content": "retrieve_blog_posts about langchain"})

