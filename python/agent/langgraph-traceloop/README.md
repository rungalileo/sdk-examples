# LangGraph + Traceloop + Galileo Integration

This example demonstrates how to add comprehensive observability to your LangGraph AI workflows using **Traceloop** (OpenLLMetry) and Galileo. Traceloop provides a simpler alternative to direct OpenTelemetry instrumentation while still giving you detailed traces showing execution flow, LLM calls, token usage, and input/output data.

## What are these tools?

**Traceloop** (also known as OpenLLMetry) is a simplified observability SDK built on top of OpenTelemetry that makes it easy to instrument LLM applications with just a few lines of code. It automatically instruments popular frameworks like OpenAI, LangChain, and more. **Galileo** provides a sophisticated platform for visualizing and analyzing your AI application traces.

### Why Traceloop?

- **Simpler setup** - Initialize with just `Traceloop.init()`
- **Automatic instrumentation** - Works with OpenAI, LangChain, LangGraph, Anthropic, and more
- **Less boilerplate** - No need to manually configure TracerProviders and SpanProcessors
- **Built-in best practices** - Follows OpenTelemetry semantic conventions automatically

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
GALILEO_API_KEY=your_galileo_api_key_here

# Your Galileo project name
GALILEO_PROJECT=your_project_name

# Log stream for organizing traces
GALILEO_LOG_STREAM=langgraph-traceloop

# Galileo console URL (if using a custom deployment is different than https://app.galileo.ai)
GALILEO_CONSOLE_URL=https://app.galileo.ai

# Your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GALILEO_API_KEY` | Yes | Your Galileo API key from [settings](https://app.galileo.ai/settings/api-keys) |
| `GALILEO_PROJECT` | Yes | Galileo project name (create one in your dashboard) |
| `GALILEO_LOG_STREAM` | Yes | Log stream name for organizing traces (default: "default") |
| `OPENAI_API_KEY` | Yes | Your OpenAI API key from [OpenAI](https://platform.openai.com/api-keys) |

### Run

```bash
uv run python main.py
```

This runs a question-answering LangGraph workflow with comprehensive Traceloop tracing. Check your Galileo project for detailed traces!

## Workflow Overview

The example implements a 3-step question-answering workflow:

1. **Input Validation** (`validate_input`) - Validates and prepares the user's question
2. **Response Generation** (`generate_response`) - Calls OpenAI GPT-3.5-turbo to generate an answer
3. **Answer Formatting** (`format_answer`) - Extracts and formats the final answer

### Trace Hierarchy

In Galileo, you'll see a clean trace structure:

```
└── astronomy_qa_session [Question → Final Answer]
    ├── LangGraph [Workflow execution]
    │   ├── validate_input [Input validation]
    │   ├── generate_response [LLM processing]
    │   └── format_answer [Answer formatting]
    └── gpt-3.5-turbo [Detailed OpenAI API call]
        ├── Token usage (prompt/completion/total)
        ├── Model parameters (temperature, max_tokens)
        └── Input/output messages
```

### Key Observability Benefits

- **Complete Input/Output Visibility** - See data flowing through each step  
- **LLM Call Details** - Token usage, model parameters, and timing
- **Session Context** - Grouped operations with meaningful metadata
- **Error Tracking** - Automatic error capture and status tracking
- **Performance Insights** - Timing for each workflow step

### Trace Attributes

Each span includes rich metadata:

- **Session Level**: Question, answer, domain (astronomy), type (Q&A)
- **Node Level**: Input/output values, node type, processing details
- **LLM Level**: Model name, tokens, temperature, messages, vendor

## Traceloop vs OpenTelemetry

This project demonstrates using Traceloop (OpenLLMetry) for instrumentation. If you want to see the equivalent implementation using direct OpenTelemetry APIs, check out the sister project:

- **langgraph-traceloop** (this project) - Simple Traceloop SDK
- **langgraph-open-telemetry** - Direct OpenTelemetry instrumentation

### Setup Comparison

**With Traceloop** (3 lines):
```python
from traceloop.sdk import Traceloop

Traceloop.init(app_name="my-app")
# Done! OpenAI and LangChain are automatically instrumented
```

**With OpenTelemetry** (20+ lines):
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

# Create and configure tracer provider
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)

# Add span processors
tracer_provider.add_span_processor(BatchSpanProcessor(...))

# Instrument frameworks
OpenAIInstrumentor().instrument()
LangchainInstrumentor().instrument()
# ... more configuration
```

Both approaches give you the same high-quality traces in Galileo!

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

