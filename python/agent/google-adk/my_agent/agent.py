"""Agent logic for the Google ADK example."""

from pathlib import Path

from dotenv import load_dotenv
from opentelemetry.sdk import trace as trace_sdk
from splunk_ao.otel import SplunkAOSpanProcessor
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from google.adk.agents import LlmAgent

load_dotenv(Path(__file__).parent / ".env")

# Create tracer provider and register Splunk AO span processor
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(SplunkAOSpanProcessor())

# Instrument Google ADK with OpenInference (this captures inputs/outputs)
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)

# ---------------------------------------------------------------------------
# ADK agent definition (import after instrumentation is configured)
# ---------------------------------------------------------------------------


# Tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}


root_agent = LlmAgent(
    model="openai/gpt-4o-mini",
    name="root_agent",
    description="Tells the current time in a specified city.",
    instruction=(
        "You are a helpful assistant that tells the current time in cities. "
        "Use the 'get_current_time' tool for this purpose."
    ),
    tools=[get_current_time],
)
