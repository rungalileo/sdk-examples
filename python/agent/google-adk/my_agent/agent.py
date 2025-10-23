import os

# Google ADK imports
from google.adk.agents.llm_agent import Agent

# OpenTelemetry imports
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# OpenInference imports for Google ADK instrumentation
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

from dotenv import load_dotenv

# Load the Galileo API configuration from .env file
load_dotenv()

# Configure the OTel endpoint environment variable
os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = os.getenv("GALILEO_API_ENDPOINT")

# Create the headers using the Galileo API key, project, and log stream
headers = {
   "Galileo-API-Key": os.getenv("GALILEO_API_KEY"),
   "project": os.getenv("GALILEO_PROJECT"),
   "logstream": os.getenv("GALILEO_LOG_STREAM")
}

# Store the headers in the appropriate environment variable
os.environ['OTEL_EXPORTER_OTLP_HEADERS'] = ",".join([
    f"{k}={v}" for k, v in headers.items()]
)

# Create and configure the OTLP span exporter
exporter = OTLPSpanExporter()
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

# Instrument the Google ADK with OpenTelemetry
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)

# The following code is the example quickstart from the Google ADK documentation
# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

# Agent definition
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="""
You are a helpful assistant that tells the current time in cities.
Use the 'get_current_time' tool for this purpose.
""",
    tools=[get_current_time],
)
