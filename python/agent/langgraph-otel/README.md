# LangGraph + OpenTelemetry + Galileo Integration

This example shows how to add observability to your LangGraph AI workflows using OpenTelemetry and Galileo.

## What are these tools?

**OpenTelemetry** creates traces showing what functions ran, timing, and data flow. **OpenInference** automatically instruments AI frameworks. **Galileo** visualizes and analyzes your AI application traces.

For detailed explanations and advanced patterns, see the [LangGraph OpenTelemetry cookbook](https://docs.galileo.ai/galileo/how-to-and-faq/galileo-python-logger/integrations/opentelemetry)

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
cd sdk-examples/python/agent/langgraph-otel

# Install dependencies
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### Environment variables
| Variable | Required | Description |
|----------|----------|-------------|
| `***************` | Yes | Your Galileo API key |
| `GALILEO_PROJECT` | Yes | Galileo project name |
| `GALILEO_LOG_STREAM` | No | Log stream name (default: "default") |
| `***************` | Yes | Your OpenAI API key |
| `GALILEO_CONSOLE_URL` | No | Custom Galileo URL (default: app.galileo.ai) |

### Run
```bash
uv run python main.py
```

This runs a simple LangGraph workflow with OpenTelemetry tracing. Check your Galileo project for the traces!

## What's included

- `main.py` - LangGraph workflow with OpenTelemetry tracing
- `pyproject.toml` - Dependencies (managed via UV)
- `.env.example` - Environment variable template

## Learn more

- [LangGraph OpenTelemetry cookbook](https://docs.galileo.ai/galileo/how-to-and-faq/galileo-python-logger/integrations/opentelemetry) - Detailed guide and patterns
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Galileo Documentation](https://v2docs.galileo.ai/)
- [UV Package Manager](https://docs.astral.sh/uv/)


