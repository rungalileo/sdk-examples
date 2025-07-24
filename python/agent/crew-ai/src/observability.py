"""A module to set up observability for Crew AI using OpenTelemetry and Galileo."""

import os

from openinference.instrumentation.crewai import CrewAIInstrumentor
from openinference.instrumentation.litellm import LiteLLMInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_observability():
    # Configure the otel variables to send traces to Galileo
    headers = {
        "Galileo-API-Key": os.environ.get(
            "GALILEO_API_KEY", "your_galileo_api_key_here"
        ),
        "project": os.environ.get("GALILEO_PROJECT", "crew"),
        "logstream": os.environ.get("GALILEO_LOG_STREAM", "default"),
    }
    os.environ["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = ",".join(
        [f"{k}={v}" for k, v in headers.items()]
    )
    traces_url = os.environ.get("GALILEO_CONSOLE_URL", "https://app.galileo.ai")
    os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = (
        f"{traces_url}/api/galileo/otel/traces"
    )

    # Setup tracer provider and instrumentations
    tracer_provider = trace_sdk.TracerProvider()
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)
    CrewAIInstrumentor().instrument(tracer_provider=tracer_provider)
