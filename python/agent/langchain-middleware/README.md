# LangChain Middleware Example

This example demonstrates how to use `GalileoMiddleware` to automatically log LangChain agent executions without manual callback setup.

## Overview

`GalileoMiddleware` provides drop-in logging for LangGraph agents. It automatically captures:

- Agent lifecycle events (start/completion)
- Model calls with prompts, responses, and metadata
- Tool calls with function names, arguments, and outputs

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Running the Example

```bash
python main.py
```

The agent will:

1. Create a LangChain agent with two tools (weather and stock price)
2. Invoke the agent with a question requiring both tools
3. Automatically log all interactions to Galileo using middleware

## What Gets Logged

The middleware creates a hierarchical trace with:

- **Agent node**: Tracks overall execution with input/output state
- **LLM nodes**: Logs each model call with prompts, responses, and timing
- **Tool nodes**: Records tool invocations with arguments and outputs

## Key Features

- **Zero configuration**: Add middleware to your agent and it works automatically
- **Async support**: Works seamlessly with both sync and async execution
- **Flexible**: Can use custom loggers and control trace management
- **Comprehensive**: Captures all relevant execution details

## Comparison with Callbacks

| Feature | GalileoMiddleware | GalileoCallback |
|---------|------------------|-----------------|
| Setup | Add to middleware list | Pass to each component |
| Complexity | Simple | Manual setup required |
| Best for | LangGraph agents | Complex LangChain apps |

For more details, see the [middleware documentation](https://v2docs.galileo.ai/sdk-api/third-party-integrations/langchain/middleware).
