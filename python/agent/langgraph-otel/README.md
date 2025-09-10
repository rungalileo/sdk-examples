# LangGraph + OpenTelemetry + Galileo Integration

This example demonstrates how to add comprehensive observability to your LangGraph AI workflows using OpenTelemetry and Galileo. You'll get detailed traces showing the complete execution flow, LLM calls, token usage, and input/output data.

## What are these tools?

**OpenTelemetry** is an observability framework that creates traces showing what functions ran, their timing, and data flow through your application. **OpenInference** automatically instruments AI frameworks like LangChain and OpenAI. **Galileo** provides a sophisticated platform for visualizing and analyzing your AI application traces.

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
GALILEO_LOG_STREAM=langgraph

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

This runs a question-answering LangGraph workflow with comprehensive OpenTelemetry tracing. Check your Galileo project for detailed traces!

## Workflow Overview

The example implements a 3-step question-answering workflow:

1. **Input Validation** (`validate_input`) - Validates and prepares the user's question
2. **Response Generation** (`generate_response`) - Calls OpenAI GPT-3.5 to generate an answer
3. **Answer Formatting** (`format_answer`) - Extracts and formats the final answer

### Trace Hierarchy
In Galileo, you'll see a clean trace structure:

```
└── astronomy_qa_session [Question → Final Answer]
    ├── LangGraph [Workflow execution]
    │   ├── validate_input [Input validation]
    │   ├── generate_response [LLM processing]
    │   └── format_answer [Answer formatting]
    └── gpt-3.5-turbo-0125 [Detailed OpenAI API call]
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

## What's included

- **`main.py`** - Complete LangGraph workflow with OpenTelemetry tracing
- **`pyproject.toml`** - All dependencies managed via UV
- **`.env`** - Environment variables (you'll need to add your API keys)
- **`README.md`** - This comprehensive guide

## Learn more

- [LangGraph OpenTelemetry cookbook](https://docs.galileo.ai/galileo/how-to-and-faq/galileo-python-logger/integrations/opentelemetry) - Detailed guide and patterns
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Galileo Documentation](https://v2docs.galileo.ai/)
- [UV Package Manager](https://docs.astral.sh/uv/)


