# LangGraph + OpenTelemetry + Galileo Integration

This example demonstrates how to add comprehensive observability to your LangGraph AI workflows using OpenTelemetry and Galileo. You'll get detailed traces showing the complete execution flow, LLM calls, token usage, and input/output data.

## What are these tools?

**OpenTelemetry** is an observability framework that creates traces showing what functions ran, their timing, and data flow through your application. The **OpenTelemetry instrumentation libraries** automatically instrument AI frameworks like LangChain and OpenAI. **Galileo** provides a sophisticated platform for visualizing and analyzing your AI application traces.

For detailed explanations and advanced patterns, see the [LangGraph OpenTelemetry cookbook](https://v2docs.galileo.ai/cookbooks/features/integrations/langgraph-otel-cookbook)

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
cd sdk-examples/python/agent/langgraph-open-telemetry

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
GALILEO_API_KEY=your_galileo_api_key_here

# Your Galileo project name
GALILEO_PROJECT=your_project_name

# Log stream for organizing traces
GALILEO_LOGSTREAM=langgraph

# Galileo console URL (if using a custom deployment is different than https://app.galileo.ai)
GALILEO_CONSOLE_URL=https://app.galileo.ai

# Your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GALILEO_API_KEY` | Yes | Your Galileo API key from [settings](https://app.galileo.ai/settings/api-keys) |
| `GALILEO_PROJECT` | Yes | Galileo project name (create one in your dashboard) |
| `GALILEO_LOGSTREAM` | Yes | Log stream name for organizing traces (default: "default") |
| `OPENAI_API_KEY` | Yes | Your OpenAI API key from [OpenAI](https://platform.openai.com/api-keys) |

### Run

```bash
uv run python main.py
```

This runs a question-answering LangGraph workflow with comprehensive OpenTelemetry tracing. Check your Galileo project for detailed traces!

## What's included

- **`main.py`** - Complete LangGraph workflow with OpenTelemetry tracing
- **`pyproject.toml`** - All dependencies managed via UV
- **`.env.example`** - Example environment variables (copy to `.env` and add your API keys)
- **`README.md`** - This comprehensive guide

## Learn more

- [LangGraph OpenTelemetry cookbook](https://v2docs.galileo.ai/cookbooks/features/integrations/langgraph-otel-cookbook)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Galileo Documentation](https://v2docs.galileo.ai/)
- [UV Package Manager](https://docs.astral.sh/uv/)
