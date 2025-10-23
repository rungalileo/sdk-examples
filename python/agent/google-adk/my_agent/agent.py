
import os
from google.adk.agents.llm_agent import Agent

from dotenv import load_dotenv

from opentelemetry.sdk import trace as trace_sdk
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

load_dotenv()

os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = os.getenv("GALILEO_API_ENDPOINT")

headers = {
   "Galileo-API-Key": os.getenv("GALILEO_API_KEY"),
   "project": os.getenv("GALILEO_PROJECT"),
   "logstream": os.getenv("GALILEO_LOG_STREAM")
}

os.environ['OTEL_EXPORTER_OTLP_HEADERS'] = ",".join([f"{k}={v}" for k, v in headers.items()])

tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(os.getenv("GALILEO_API_ENDPOINT"))))

# Optional: log locally
if os.getenv("CONSOLE_OTEL_ENABLED") == "true":
    tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

# Register the provider
trace_api.set_tracer_provider(tracer_provider=tracer_provider)

GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    tools=[get_current_time],
)
