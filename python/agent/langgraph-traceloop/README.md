# LangGraph + Traceloop + Galileo Integration

This example demonstrates how to add comprehensive observability to your LangGraph AI workflows using **Traceloop** (OpenLLMetry) and Galileo. Traceloop provides a simpler alternative to direct OpenTelemetry instrumentation while still giving you detailed traces showing execution flow, LLM calls, token usage, and input/output data.

## What are these tools?

**Traceloop** (also known as OpenLLMetry) is a simplified observability SDK built on top of OpenTelemetry that makes it easy to instrument LLM applications with just a few lines of code. It automatically instruments popular frameworks like OpenAI, LangChain, and more. **Galileo** provides a sophisticated platform for visualizing and analyzing your AI application traces.

## Quick start

### Prerequisites

- Python 3.12+
- [UV package manager](https://docs.astral.sh/uv/getting-started/installation/)
- [Galileo account](https://app.galileo.ai) (free)
- OpenAI API key

### Installation

```bash
# Clone and navigate
git clone https://github.com/rungalileo/sdk-examples
cd sdk-examples/python/agent/langgraph-traceloop

# Install dependencies
uv sync

# Create environment file
cp .env.example .env
# Edit .env with your API keys (see below)
```

### Environment variables

Create a `.env` file in the project root with the following variables:

```bash
# Your Galileo API key (get from https://app.galileo.ai/settings/api-keys)

TRACELOOP_BASE_URL=https://api.galileo.ai/otel

TRACELOOP_HEADERS="Galileo-API-Key=your_galileo_api_key_here, project=traceloop, logstream=default, X-Use-Otel-New=true"

# Your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

| Variable             | Required | Description                                                             |
| -------------------- | -------- | ----------------------------------------------------------------------- |
| `TRACELOOP_BASE_URL` | Yes      | The base URL for the Traceloop Client it will send traces to galileo    |
| `TRACELOOP_HEADERS`  | Yes      | The headers for the Traceloop Client to send to galileo                 |
| `OPENAI_API_KEY`     | Yes      | Your OpenAI API key from [OpenAI](https://platform.openai.com/api-keys) |

### Run

```bash
uv run python main.py
```

This runs a question-answering LangGraph workflow with comprehensive Traceloop tracing. Check your Galileo project for detailed traces!

## What's included

- **`main.py`** - Complete LangGraph workflow with Traceloop instrumentation
- **`pyproject.toml`** - All dependencies managed via UV
- **`.env.example`** - Example environment variables (copy to `.env` and add your API keys)
- **`README.md`** - This comprehensive guide

## Learn more

- [Traceloop Documentation](https://traceloop.com/docs/openllmetry/getting-started-python)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Galileo Documentation](https://v2docs.galileo.ai/)
- [UV Package Manager](https://docs.astral.sh/uv/)
