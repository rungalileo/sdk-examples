import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

# load environment variables from .env file
import dotenv
dotenv.load_dotenv()

# Authenticate your headers with your current OTEL setup.
headers = {
    "Galileo-API-Key": os.environ.get("GALILEO_API_KEY"),
    "project": os.environ.get("GALILEO_PROJECT"),
    "logstream": os.environ.get("GALILEO_LOG_STREAM", "default"),
}
os.environ["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = ",".join(
    [f"{k}={v}" for k, v in headers.items()]
)
traces_url = os.environ.get("GALILEO_CONSOLE_URL", "https://app.galileo.ai")
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = (
    f"{traces_url}/api/galileo/otel/traces"
)

# ---------- 1) Configure OpenTelemetry ----------
resource = Resource.create({"service.name": "langgraph-agent"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


# ---------- 2) Define state & nodes ----------
class AgentState(TypedDict, total=False):
    # LangGraph state is a mapping; TypedDict keeps us honest
    query: str
    response: str


def initial_node(state: AgentState):
    # Child of any current span; here we start a dedicated one per node
    with tracer.start_as_current_span("initial_node") as span:
        q = state.get("query", "")
        span.set_attribute("input.query", q)
        # span events are great for breadcrumbs
        span.add_event("received_query", {"len": len(q)})
        # Must return a partial state update
        return {"query": q}


def processing_node(state: AgentState):
    with tracer.start_as_current_span("processing_node") as span:
        q = state["query"]
        # “Business logic”
        processed = f"Processed: {q.upper()}"
        # Attributes are indexed in backends; prefer small string/number values
        span.set_attribute("processed.preview", processed[:50])
        span.add_event("computed_response")
        return {"response": processed}


# ---------- 3) Build the graph ----------
workflow = StateGraph(AgentState)
workflow.add_node("initial", initial_node)
workflow.add_node("process", processing_node)

workflow.set_entry_point("initial")
workflow.add_edge("initial", "process")
workflow.add_edge("process", END)

app = workflow.compile()

# ---------- 4) Invoke & observe ----------
if __name__ == "__main__":
    inputs = {"query": "hello world"}
    result = app.invoke(inputs)
    print(f"LangGraph result: {result}")
