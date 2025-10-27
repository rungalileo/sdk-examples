# Vercel AI Agent with Galileo Observability

This example demonstrates how to build an AI agent using the Vercel AI SDK with Galileo observability integration. The agent can retrieve weather information and perform temperature conversions using tool calling.

## Features

- **Vercel AI SDK Agent**: Uses the experimental Agent API from Vercel AI SDK
- **Tool Calling**: Implements custom tools for weather lookup and temperature conversion
- **Galileo Observability**: Integrated with OpenTelemetry to track agent execution, tool calls, and performance
- **Type Safety**: Leverages Zod schemas for type-safe tool definitions
- **OpenAI Integration**: Uses GPT-4-turbo model for intelligent agent responses

## Prerequisites

- Node.js 18+ installed
- OpenAI API key
- Galileo API key (sign up at [https://app.galileo.ai](https://app.galileo.ai))

## Installation

1. Clone the repository and navigate to this example:

```bash
cd typescript/agent/vercel-agent
```

2. Install dependencies:

```bash
npm install
```

3. Set up environment variables:

Create a `.env` file in the root directory with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Galileo Configuration
GALILEO_API_KEY=your-galileo-api-key
GALILEO_PROJECT=your-project-name
GALILEO_CONSOLE_URL=https://app.galileo.ai
GALILEO_LOG_STREAM=default
```

## Usage

### Run the example

```bash
npm start
```

### Development mode with auto-reload

```bash
npm run dev
```

### Build the project

```bash
npm run build
```

## How It Works

### Agent Setup

The agent is configured with two custom tools:

1. **Weather Tool**: Retrieves weather information for a given location (returns temperature in Fahrenheit)
2. **Temperature Converter**: Converts temperature from Fahrenheit to Celsius

```typescript
const weatherAgent = new Agent({
  model: openai('gpt-4-turbo'),
  tools: {
    weather: tool({...}),
    convertFahrenheitToCelsius: tool({...}),
  },
  stopWhen: stepCountIs(20),
  experimental_telemetry: { isEnabled: true },
});
```

### Galileo Integration

The example uses OpenTelemetry to send traces to Galileo:

1. **Setup**: The `setupOtel.ts` file configures the OpenTelemetry SDK with Galileo's OTLP endpoint
2. **Automatic Tracing**: When `experimental_telemetry` is enabled, the Vercel AI SDK automatically generates telemetry data
3. **Observability**: View agent execution, tool calls, latencies, and errors in the Galileo dashboard

### Example Query

The agent handles complex queries like:

```typescript
"What is the weather in San Francisco in celsius?"
```

The agent will:

1. Use the `weather` tool to get the temperature in Fahrenheit
2. Use the `convertFahrenheitToCelsius` tool to convert the temperature
3. Return a natural language response with the temperature in Celsius

## Project Structure

```
vercel-agent/
├── src/
│   ├── index.ts         # Main agent implementation
│   └── setupOtel.ts     # OpenTelemetry configuration for Galileo
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript configuration
└── README.md           # This file
```

## Key Dependencies

- **ai**: Vercel AI SDK for building AI agents
- **@ai-sdk/openai**: OpenAI provider for Vercel AI SDK
- **@vercel/otel**: Vercel's OpenTelemetry package for optimized trace export
- **@opentelemetry/sdk-node**: OpenTelemetry SDK for Node.js
- **zod**: Type-safe schema validation for tool inputs

## Viewing Results in Galileo

After running the agent:

1. Log in to your Galileo account at [https://app.galileo.ai](https://app.galileo.ai)
2. Navigate to your project (specified in `GALILEO_PROJECT`)
3. View the agent's execution traces, including:
   - Agent steps and reasoning
   - Tool calls with inputs and outputs
   - Latency metrics
   - Token usage
   - Any errors or warnings

## Customization

### Adding New Tools

You can extend the agent with additional tools by adding them to the `tools` object:

```typescript
tools: {
  weather: tool({...}),
  convertFahrenheitToCelsius: tool({...}),
  yourNewTool: tool({
    description: 'Description of what your tool does',
    inputSchema: z.object({
      param: z.string().describe('Parameter description'),
    }),
    execute: async ({ param }) => {
      // Your tool logic here
      return { result: 'value' };
    },
  }),
}
```

### Changing the Model

Replace `openai('gpt-4-turbo')` with any supported model:

```typescript
openai('gpt-4o')           // Latest GPT-4 Omni
openai('gpt-4o-mini')      // Smaller, faster GPT-4 Omni
openai('gpt-3.5-turbo')    // GPT-3.5 Turbo
```

### Adjusting Step Limits

Modify the `stopWhen` condition to control agent behavior:

```typescript
stopWhen: stepCountIs(10)  // Stop after 10 steps
```

## Troubleshooting

### OpenTelemetry Debug Logs

If traces aren't appearing in Galileo, enable debug logging in `setupOtel.ts`:

```typescript
diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);
```

### Common Issues

- **Missing API Keys**: Ensure all required environment variables are set
- **Network Issues**: Check that your application can reach Galileo's endpoint
- **Telemetry Not Enabled**: Verify `experimental_telemetry: { isEnabled: true }` is set in the agent configuration

## Learn More

- [Vercel AI SDK Documentation](https://sdk.vercel.ai/docs)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
