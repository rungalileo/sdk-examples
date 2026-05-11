from random import randint
from typing import Annotated

from agent_framework import openai, tool
from agent_framework.observability import enable_instrumentation
from galileo.otel import GalileoSpanProcessor, add_galileo_span_processor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from pydantic import Field

# Set up the OTel tracer provider with the Galileo span processor
tracer_provider = TracerProvider()
galileo_processor = GalileoSpanProcessor()
add_galileo_span_processor(tracer_provider, galileo_processor)
trace.set_tracer_provider(tracer_provider)

# Enable the Microsoft Agent Framework's built-in OTel instrumentation.
# Set enable_sensitive_data=True to send LLM inputs and outputs to Galileo.
# If set to False, only span metadata (timing, token counts, etc.) will be sent.
enable_instrumentation(enable_sensitive_data=True)


# The following code is the basic tool call example from the
# Microsoft Agent Framework documentation
# https://github.com/microsoft/agent-framework


@tool(approval_mode="never_require")
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}C."


client = openai.OpenAIChatClient(model_id="gpt-4.1-mini")

agent = client.as_agent(
    name="WeatherAgent",
    instructions="You are a helpful weather agent. Use the get_weather tool to answer questions.",
    tools=[get_weather],
)


async def main():
    result = await agent.run("What's the weather like in Seattle?")
    print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
