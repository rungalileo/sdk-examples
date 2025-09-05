import os
from typing import TypedDict

# Load environment variables first (contains API keys and project settings)
import dotenv
dotenv.load_dotenv()

# ============================================================================
# OPENTELEMETRY & GALILEO IMPORTS
# ============================================================================
# OpenTelemetry (OTel) is an observability framework that helps you collect
# traces, metrics, and logs from your applications. Think of it as a way to
# "instrument" your code so you can see exactly what's happening during execution.

# Core OpenTelemetry imports
from opentelemetry.sdk import trace as trace_sdk     # SDK for creating traces
from opentelemetry import trace as trace_api         # API for interacting with traces
from opentelemetry.sdk.trace.export import BatchSpanProcessor  # Efficiently batches spans before export
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # Sends traces via HTTP
from opentelemetry.sdk.trace.export import ConsoleSpanExporter  # Prints traces to console (for debugging)

# OpenInference is a specialized instrumentation library that understands AI frameworks
# It automatically creates meaningful spans for LangChain/LangGraph operations
from openinference.instrumentation.langchain import LangChainInstrumentor

# LangGraph imports - this is what we're actually instrumenting
from langgraph.graph import StateGraph, END

# ============================================================================
# STEP 1: CONFIGURE GALILEO AUTHENTICATION
# ============================================================================
# Galileo is an AI observability platform that helps you monitor and debug
# AI applications. It receives and visualizes the traces we'll generate.

# Set up authentication headers for Galileo
# These tell Galileo who you are and which project to store traces in
headers = {
    "Galileo-API-Key": os.environ.get("GALILEO_API_KEY"),      # Your unique API key
    "project": os.environ.get("GALILEO_PROJECT"),              # Which Galileo project to use
    "logstream": os.environ.get("GALILEO_LOG_STREAM", "default"),  # Organize traces within the project
}

# OpenTelemetry requires headers in a specific format: "key1=value1,key2=value2"
# This converts our dictionary to that format
os.environ["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = ",".join(
    [f"{k}={v}" for k, v in headers.items()]
)

# Debug: Print the formatted headers to verify they're correct
print(f"OTEL Headers: {os.environ['OTEL_EXPORTER_OTLP_TRACES_HEADERS']}")

# ============================================================================
# STEP 2: CONFIGURE OPENTELEMETRY TRACING
# ============================================================================
# OpenTelemetry works by creating "spans" - units of work that represent operations
# in your application. Spans are organized into "traces" that show the full flow
# of a request through your system.

# Define where to send the traces - Galileo's OpenTelemetry endpoint
endpoint = "https://app.galileo.ai/api/galileo/otel/traces"

# Create a TracerProvider - this is the main entry point for OpenTelemetry
# Think of it as the "manager" that coordinates all tracing activity
tracer_provider = trace_sdk.TracerProvider()

# Add a span processor that sends traces to Galileo
# BatchSpanProcessor is more efficient than SimpleSpanProcessor for production
# because it batches multiple spans together before sending
tracer_provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(endpoint)  # OTLP = OpenTelemetry Protocol
    )
)

# OPTIONAL: Also send traces to console for local debugging
# Comment out the next two lines if you don't want console output
tracer_provider.add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

# Register our tracer provider as the global one
# This means all OpenTelemetry operations will use our configuration
trace_api.set_tracer_provider(tracer_provider=tracer_provider)

# ============================================================================
# STEP 3: APPLY OPENINFERENCE INSTRUMENTATION
# ============================================================================
# OpenInference automatically instruments LangChain/LangGraph to create spans
# for AI operations. This gives us detailed visibility into:
# - LangGraph workflow execution
# - Individual node processing
# - State transitions
# - Input/output data
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
print("✓ LangGraph instrumentation applied - automatic spans will be created")

# Get a tracer for creating custom spans manually
# We'll use this in our node functions below
tracer = trace_api.get_tracer(__name__)


# ============================================================================
# STEP 4: DEFINE THE LANGGRAPH STATE AND NODES
# ============================================================================
# LangGraph uses a shared state object (a dict) that flows through nodes. Each
# node reads from the state and can write updates back to it.
class AgentState(TypedDict, total=False):
    query: str    # The user's input
    response: str # The processed response

# Node 1: Validate/record the input
# We also create a custom span here to show how to add attributes & events
# Manually created spans give you fine-grained observability alongside the
# automatic spans from OpenInference.
def initial_node(state: AgentState):
    # Create a child span for this node's work
    with tracer.start_as_current_span("initial_node") as span:
        q = state.get("query", "")
        span.set_attribute("input.query", q)     # Small strings/numbers are best for attributes
        span.add_event("received_query", {"len": len(q)})  # Events act like breadcrumbs
        return {"query": q}

# Node 2: Perform business logic
# Here we transform the input and record a preview as a span attribute
def processing_node(state: AgentState):
    with tracer.start_as_current_span("processing_node") as span:
        q = state["query"]
        processed = f"Processed: {q.upper()}"
        span.set_attribute("processed.preview", processed[:50])
        span.add_event("computed_response")
        return {"response": processed}

# ============================================================================
# STEP 5: BUILD AND RUN THE LANGGRAPH WORKFLOW
# ============================================================================
workflow = StateGraph(AgentState)
workflow.add_node("initial", initial_node)
workflow.add_node("process", processing_node)

# Entry point and edges define the control flow of the graph
workflow.set_entry_point("initial")
workflow.add_edge("initial", "process")
workflow.add_edge("process", END)

# Compile builds the runnable app
app = workflow.compile()

# Run the app and observe traces in both console and Galileo
if __name__ == "__main__":
    inputs = {"query": "hello world"}
    result = app.invoke(inputs)
    print(f"LangGraph result: {result}")
    print("✓ Execution complete - check Galileo for traces in your project/log stream")
