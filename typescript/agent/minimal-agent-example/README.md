# Galileo TypeScript Agent

This is a minimal TypeScript agent implementation that uses Galileo for logging tool and LLM spans. The agent can convert text numbers to numerical values and perform arithmetic calculations.

## Features

- Converts text numbers to numerical values (e.g., "seven" to 7)
- Performs arithmetic calculations (e.g., "4 + 7")
- Uses Galileo for logging tool and LLM spans
- Implements a proper agent loop where tool selection happens after each tool execution

## Setup

1. Install dependencies:

```bash
npm install
```

2. Create a `.env` file based on the `.env.example` file:

```bash
cp .env.example .env
```

3. Add your OpenAI API key and Galileo API key to the `.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
GALILEO_API_KEY=your_galileo_api_key_here
```

## Running the Agent

To run the agent:

```bash
npm start
```

Or with TypeScript directly:

```bash
npx ts-node minimal_agent.ts
```

## Development

For development with auto-reload:

```bash
npm run dev
```

To build the TypeScript code:

```bash
npm run build
```

## How It Works

1. The agent uses the `@log` decorator from Galileo to log tool and LLM spans.
2. When a query is received, the agent:
   - Calls the LLM to determine which tools to use
   - Executes the selected tool
   - Feeds the result back to the LLM
   - Repeats until the task is complete
3. The agent can handle two types of tools:
   - `convert_text_to_arithmetic_expression`: Converts text numbers to numerical expressions
   - `calculate`: Performs arithmetic calculations

## Span Hierarchy

The span hierarchy created by the agent looks like:

- `processQuery` (LLM span)
  - `convertTextToArithmeticExpression` (tool span)
  - `calculate` (tool span)

This hierarchy accurately represents the flow of operations in the agent. 