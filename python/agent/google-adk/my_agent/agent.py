# Load env vars FIRST, before any other imports that depend on them
from dotenv import load_dotenv

load_dotenv()

# OpenTelemetry imports
from opentelemetry.sdk import trace as trace_sdk

# Galileo span processor (auto-configures OTLP headers & endpoint from env vars)
from galileo import otel

# OpenInference instrumentation for Google ADK (captures inputs/outputs)
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# Create tracer provider and register Galileo span processor
tracer_provider = trace_sdk.TracerProvider()
galileo_span_processor = otel.GalileoSpanProcessor()
tracer_provider.add_span_processor(galileo_span_processor)

# Instrument Google ADK with OpenInference (this captures inputs/outputs)
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)

# ---------------------------------------------------------------------------
# ADK agent definition (import after instrumentation is configured)
# This exapple is from the Google ADK Python Quickstart documentation:
# https://google.github.io/adk-docs/get-started/python/
# ---------------------------------------------------------------------------

from google.adk.agents.llm_agent import Agent


# Tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="root_agent",
    description="Tells the current time in a specified city.",
    instruction=("You are a helpful assistant that tells the current time in cities. " "Use the 'get_current_time' tool for this purpose."),
    tools=[get_current_time],
)
