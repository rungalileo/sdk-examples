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
from opentelemetry.sdk import trace as trace_sdk  # SDK for creating traces
from opentelemetry import trace as trace_api  # API for interacting with traces
from opentelemetry.sdk.trace.export import BatchSpanProcessor  # Efficiently batches spans before export
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # Sends traces via HTTP
from opentelemetry.sdk.trace.export import ConsoleSpanExporter  # Prints traces to console (for debugging)

# OpenInference is a specialized instrumentation library that understands AI frameworks
# It automatically creates meaningful spans for LangChain/LangGraph operations
from openinference.instrumentation.langchain import LangChainInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor

# LangGraph imports - this is what we're actually instrumenting
from langgraph.graph import StateGraph, END

# OpenAI imports for LLM integration
import openai

# ============================================================================
# STEP 1: CONFIGURE API AUTHENTICATION
# ============================================================================
# Configure OpenAI API key
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
client = openai.OpenAI(api_key=openai_api_key)
print("✓ OpenAI client configured")

# Galileo is an AI observability platform that helps you monitor and debug
# AI applications. It receives and visualizes the traces we'll generate.

# Set up authentication headers for Galileo
# These tell Galileo who you are and which project to store traces in
headers = {
    "Galileo-API-Key": os.environ.get("GALILEO_API_KEY"),  # Your unique API key
    "project": os.environ.get("GALILEO_PROJECT"),  # Which Galileo project to use
    "logstream": os.environ.get("GALILEO_LOG_STREAM", "default"),  # Organize traces within the project
}

# OpenTelemetry requires headers in a specific format: "key1=value1,key2=value2"
# This converts our dictionary to that format
os.environ["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = ",".join([f"{k}={v}" for k, v in headers.items()])

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

# Create a TracerProvider with descriptive resource information
# This helps identify these traces as coming from OpenTelemetry in Galileo
from opentelemetry.sdk.resources import Resource

resource = Resource.create({"service.name": "LangGraph-OpenTelemetry-Demo", "service.version": "1.0.0", "deployment.environment": "development"})
tracer_provider = trace_sdk.TracerProvider(resource=resource)

# Add a span processor that sends traces to Galileo
# BatchSpanProcessor is more efficient than SimpleSpanProcessor for production
# because it batches multiple spans together before sending
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint)))  # OTLP = OpenTelemetry Protocol

# OPTIONAL: Console output disabled to reduce noise in Galileo
# Uncomment the next 3 lines if you want local console debugging:
# tracer_provider.add_span_processor(
#     BatchSpanProcessor(ConsoleSpanExporter())
# )

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

# Also instrument OpenAI calls to capture LLM input/output
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
print("✓ OpenAI instrumentation applied - LLM calls will be traced")

# Get a tracer for creating custom spans manually
# We'll use this in our node functions below
tracer = trace_api.get_tracer(__name__)


# ============================================================================
# STEP 4: DEFINE THE LANGGRAPH STATE AND NODES
# ============================================================================
# LangGraph uses a shared state object (a dict) that flows through nodes. Each
# node reads from the state and can write updates back to it.
class AgentState(TypedDict, total=False):
    user_input: str  # The user's input question
    llm_response: str  # The raw response from the LLM
    parsed_answer: str  # The processed/cleaned answer


# Node 1: Input Validation
# Validates and prepares the user input for processing
def validate_input(state: AgentState):
    user_input = state.get("user_input", "")
    print(f"📥 Validating input: '{user_input}'")
    
    # Add span attributes for better observability
    current_span = trace_api.get_current_span()
    if current_span:
        current_span.set_attribute("input.value", str(state))
        current_span.set_attribute("output.value", user_input)
        current_span.set_attribute("node.type", "validation")
    
    return {"user_input": user_input}


# Node 2: Generate Response
# Calls OpenAI to generate a response to the user's question
# OpenAI instrumentation will automatically create detailed spans
def generate_response(state: AgentState):
    user_input = state["user_input"]
    
    try:
        print(f"⚙️ Calling OpenAI with: '{user_input}'")
        
        # Make the OpenAI API call - OpenAI instrumentation handles tracing
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_input}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Extract the response content
        llm_response = response.choices[0].message.content
        
        print(f"✓ Received response: '{llm_response[:100]}...'")
        
        return {"llm_response": llm_response}
        
    except Exception as e:
        print(f"❌ Error calling OpenAI: {e}")
        return {"llm_response": f"Error: {str(e)}"}


# Node 3: Format Answer
# Extracts and formats a clean answer from the raw LLM response
def format_answer(state: AgentState):
    llm_response = state.get("llm_response", "")
    
    # Simple parsing - extract first sentence for a concise answer
    sentences = llm_response.split('. ')
    parsed_answer = sentences[0] if sentences else llm_response
    
    # Clean up the answer
    parsed_answer = parsed_answer.strip()
    if not parsed_answer.endswith('.') and parsed_answer:
        parsed_answer += '.'
    
    print(f"✨ Parsed answer: '{parsed_answer}'")
    
    # Add span attributes for better observability
    current_span = trace_api.get_current_span()
    if current_span:
        current_span.set_attribute("input.value", llm_response)
        current_span.set_attribute("output.value", parsed_answer)
        current_span.set_attribute("node.type", "formatting")
    
    return {"parsed_answer": parsed_answer}


# ============================================================================
# STEP 5: BUILD AND RUN THE LANGGRAPH WORKFLOW
# ============================================================================
workflow = StateGraph(AgentState)
workflow.add_node("validate_input", validate_input)
workflow.add_node("generate_response", generate_response)
workflow.add_node("format_answer", format_answer)

# Entry point and edges define the control flow of the graph
workflow.set_entry_point("validate_input")
workflow.add_edge("validate_input", "generate_response")
workflow.add_edge("generate_response", "format_answer")
workflow.add_edge("format_answer", END)

# Compile builds the runnable app
app = workflow.compile()

# Run the app and observe traces in both console and Galileo
if __name__ == "__main__":
    # Create a session-level span to group all operations
    with tracer.start_as_current_span("astronomy_qa_session") as session_span:
        inputs = {"user_input": "what moons did galileo discover"}
        
        # Add OpenInference-compatible attributes for proper input/output display
        session_span.set_attribute("input.value", inputs["user_input"])
        session_span.set_attribute("input.mime_type", "text/plain")
        session_span.set_attribute("session.type", "question_answering")
        session_span.set_attribute("session.domain", "astronomy")
        
        result = app.invoke(inputs)
        
        # Add result attributes with OpenInference-compatible format
        if result.get('llm_response'):
            final_answer = result.get('parsed_answer', result.get('llm_response'))
            session_span.set_attribute("output.value", final_answer)
            session_span.set_attribute("output.mime_type", "text/plain")
            session_span.set_status(trace_api.Status(trace_api.StatusCode.OK))
        else:
            session_span.set_status(trace_api.Status(trace_api.StatusCode.ERROR, "No response generated"))
        
        print(f"\n=== FINAL RESULT ===")
        print(f"Question: {result.get('user_input', 'N/A')}")
        print(f"LLM Response: {result.get('llm_response', 'N/A')}")
        print(f"Parsed Answer: {result.get('parsed_answer', 'N/A')}")
    
    print("✓ Execution complete - check Galileo for traces in your project/log stream")
