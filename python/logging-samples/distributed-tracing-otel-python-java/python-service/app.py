import logging
import os
from typing import TypedDict

import chromadb
import chromadb.utils.embedding_functions as ef
import openai
from fastapi import FastAPI
from galileo.otel import start_galileo_span
from galileo_core.schemas.logging.span import RetrieverSpan
from galileo_core.schemas.shared.document import Document
from langgraph.graph import END, START, StateGraph
from openinference.instrumentation.langchain import LangChainInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# OTel setup — export to the local OpenTelemetry Collector, which forwards
# to Galileo. The collector owns Galileo credentials; this service does not.
#
# Defaults to http://localhost:4318 for running outside Docker. In
# docker-compose, OTEL_EXPORTER_OTLP_ENDPOINT is overridden to the collector
# service address.
# ---------------------------------------------------------------------------
_otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
_otlp_exporter = OTLPSpanExporter(endpoint=f"{_otlp_endpoint.rstrip('/')}/v1/traces")

provider = TracerProvider(resource=Resource.create())
# BatchSpanProcessor batches spans and flushes them on a repeating timer.
# The default interval is 5000ms, which means Python spans can appear in
# Galileo up to 5 seconds after Java spans for the same request. Reducing
# this to 1000ms keeps the trace UI consistent without adding per-request latency.
provider.add_span_processor(BatchSpanProcessor(_otlp_exporter, schedule_delay_millis=1000))
trace.set_tracer_provider(provider)

# ---------------------------------------------------------------------------
# Instrumentation strategy
# ---------------------------------------------------------------------------
# We rely on auto-instrumentation wherever possible and only add manual
# Galileo spans when auto-instrumentation can't express what we need:
#
#   Auto-instrumented (no code changes required):
#     - FastAPI server spans            -> opentelemetry-instrumentation-fastapi
#     - LangGraph workflow + node spans -> openinference-instrumentation-langchain
#       (LangChain instrumentor covers LangGraph; there is no separate
#        LangGraph instrumentor package on PyPI.)
#     - OpenAI chat / embeddings spans  -> openinference-instrumentation-openai
#
#   Manual Galileo spans (see retrieve_documents below):
#     - RetrieverSpan around ChromaDB queries — needed for two reasons:
#         1. ChromaDB has no OTel/OpenInference instrumentation package, so
#            without a manual span the retrieval step would be invisible.
#         2. RetrieverSpan is a Galileo-specific span type that renders
#            retrieved documents as source context in the trace UI. A
#            generic OTel span cannot produce this UI treatment.
# ---------------------------------------------------------------------------
LangChainInstrumentor().instrument(tracer_provider=provider)
OpenAIInstrumentor().instrument(tracer_provider=provider)

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
oai = openai.OpenAI()
chroma = chromadb.HttpClient(
    host=os.getenv("CHROMADB_HOST", "localhost"),
    port=int(os.getenv("CHROMADB_PORT", "8000")),
)
embedding_fn = ef.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small",
)

CHROMA_COLLECTION = "financial_docs"


# ---------------------------------------------------------------------------
# LangGraph state & nodes
# ---------------------------------------------------------------------------
class GraphState(TypedDict):
    question: str
    category: str
    documents: list[str]
    sources: list[str]
    answer: str


def route_question(state: GraphState) -> GraphState:
    """Entry node — logs the category and passes state through."""
    logger.info("Routing: category=%s", state["category"])
    return {**state, "documents": [], "sources": []}


def retrieve_documents(state: GraphState) -> GraphState:
    """Query ChromaDB for relevant documents.

    This is the one place we create a manual Galileo span. See the
    "Instrumentation strategy" comment above for the rationale. The
    RetrieverSpan's `output` is populated with a list of Documents so the
    Galileo UI can render each retrieved chunk as inline source context.
    """
    query = state["question"]
    retriever_span = RetrieverSpan(name="chromadb_search", input=query)

    with start_galileo_span(retriever_span) as span:
        try:
            collection = chroma.get_collection(CHROMA_COLLECTION, embedding_function=embedding_fn)
            results = collection.query(query_texts=[query], n_results=3)
            docs = results["documents"][0] if results["documents"] else []
            ids = results["ids"][0] if results["ids"] else []
        except Exception:
            logger.exception("ChromaDB query failed, continuing with empty context")
            docs, ids = [], []

        retriever_span.output = [Document(content=d, metadata={"id": i}) for d, i in zip(docs, ids)]
        span.set_attribute("retriever.result_count", len(docs))
        logger.info("Retrieved %d documents", len(docs))

    return {**state, "documents": docs, "sources": ids}


def generate_answer(state: GraphState) -> GraphState:
    """Call OpenAI with retrieved context to produce the final answer.

    OpenAIInstrumentor automatically creates an LLM span for this call,
    capturing model, token usage, and input/output content.
    """
    question = state["question"]
    docs = state.get("documents", [])

    context_block = "\n\n---\n\n".join(docs) if docs else "No additional context available."
    messages = [
        {
            "role": "system",
            "content": (
                "You are a knowledgeable financial services assistant. "
                "Answer the user's question using ONLY the provided context. "
                "If the context doesn't contain enough information, say so."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context_block}\n\nQuestion: {question}",
        },
    ]

    response = oai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
    )
    # message.content is Optional[str] — guard against content filters or
    # tool-call responses where the model returns no text.
    answer = response.choices[0].message.content or ""
    logger.info("Generated answer (%d chars)", len(answer))
    return {**state, "answer": answer}


# ---------------------------------------------------------------------------
# Build the LangGraph workflow
# ---------------------------------------------------------------------------
graph_builder = StateGraph(GraphState)
graph_builder.add_node("route", route_question)
graph_builder.add_node("retrieve", retrieve_documents)
graph_builder.add_node("generate", generate_answer)

graph_builder.add_edge(START, "route")
graph_builder.add_edge("route", "retrieve")
graph_builder.add_edge("retrieve", "generate")
graph_builder.add_edge("generate", END)

workflow = graph_builder.compile()

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="Financial RAG Service")

# FastAPIInstrumentor extracts the W3C traceparent from incoming HTTP requests
# and creates a server span that becomes the parent for all spans created
# during the request — this is what stitches Python's trace onto Java's.
# Call WITHOUT the tracer_provider kwarg so it uses the global provider set
# above; passing tracer_provider explicitly can silently skip middleware
# registration in recent opentelemetry-instrumentation-fastapi versions.
FastAPIInstrumentor.instrument_app(app)


class ProcessRequest(BaseModel):
    question: str
    category: str = "GENERAL"


@app.post("/process")
def process(req: ProcessRequest):
    """Main RAG endpoint — called by the Java gateway.

    No manual workflow span is needed here: LangChainInstrumentor emits a
    `LangGraph` span covering the full `workflow.invoke(...)` call, which
    serves as the workflow container in the Galileo trace UI.
    """
    result = workflow.invoke(
        {
            "question": req.question,
            "category": req.category,
            "documents": [],
            "sources": [],
            "answer": "",
        }
    )
    return {"answer": result["answer"], "sources": result.get("sources", [])}


@app.get("/health")
def health():
    return {"status": "ok"}
