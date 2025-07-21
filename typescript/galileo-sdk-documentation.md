# Galileo SDK Documentation

## Introduction

Galileo is an observability platform for LLM applications. The Galileo SDK provides tools to monitor, debug, and improve AI systems by tracking inputs, outputs, and performance metrics. This documentation covers the installation, setup, and usage of the Galileo SDK for TypeScript/JavaScript applications.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Core Concepts](#core-concepts)
4. [API Reference](#api-reference)
   - [Initialization](#initialization)
   - [Logging](#logging)
   - [OpenAI Integration](#openai-integration)
   - [Workflow Management](#workflow-management)
   - [Utility Functions](#utility-functions)
5. [Use Cases](#use-cases)
   - [Simple Chatbot](#simple-chatbot)
   - [RAG Applications](#rag-applications)
   - [Agent Systems](#agent-systems)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

## Installation

### Standard Installation

```bash
npm install galileo
```

### Installation without Optional Dependencies

```bash
npm install galileo --no-optional
```

## Getting Started

### Basic Setup

1. Import the necessary functions from the Galileo package:

```typescript
import { init, flush, wrapOpenAI } from 'galileo';
import { OpenAI } from 'openai';
```

2. Initialize Galileo with your project and log stream names:

```typescript
init({
  projectName: 'my-project',
  logStreamName: 'development'
});
```

3. Wrap your OpenAI client for automatic logging:

```typescript
const openai = wrapOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }));
```

4. Use the wrapped client as you would normally:

```typescript
const response = await openai.chat.completions.create({
  model: "gpt-4o",
  messages: [{ content: "Hello, how can I help you today?", role: "user" }],
});
```

5. Flush logs before your application exits:

```typescript
await flush();
```

### Environment Variables

You can configure Galileo using environment variables:

```
# Galileo Environment Variables
GALILEO_API_KEY=your-galileo-api-key             # Your Galileo API key.
GALILEO_PROJECT=your-galileo-project-name        # Your Galileo project name.
GALILEO_LOG_STREAM=your-galileo-log-stream       # The name of the log stream you want to use for logging.

# Provide the console url below if you are using a custom deployment, and not using app.galileo.ai
# GALILEO_CONSOLE_URL=your-galileo-console-url   # Optional if you are using a hosted version of Galileo
```

## Core Concepts

### Traces and Spans

Galileo uses a tracing model similar to distributed tracing systems:

- **Trace**: Represents a complete user interaction or workflow
- **Span**: Represents a single operation within a trace (e.g., an LLM call, a retrieval operation, or a tool execution)

### Span Types

Galileo supports several span types:

- **LLM**: For language model interactions
- **Retriever**: For document retrieval operations in RAG systems
- **Tool**: For function calls and tool usage
- **Workflow**: For grouping related spans

## API Reference

### Initialization

#### `init(options)`

Initializes the Galileo client with project and log stream information.

```typescript
init({
  projectName: 'my-project',
  logStreamName: 'development'
});
```

Parameters:
- `options.projectName` (optional): The name of your project
- `options.logStreamName` (optional): The name of your log stream

If not provided, these values will be read from environment variables `GALILEO_PROJECT` and `GALILEO_LOG_STREAM`.

#### `flush()`

Uploads all captured traces to the Galileo platform.

```typescript
await flush();
```

### Logging

#### `log(options, fn)`

Wraps a function to log its execution as a span in Galileo.

```typescript
const myLoggedFunction = log(
  { spanType: 'tool', name: 'my-function' },
  async (param1, param2) => {
    // Function implementation
    return result;
  }
);
```

Parameters:
- `options.spanType`: The type of span ('llm', 'retriever', 'tool', or 'workflow')
- `options.name`: A name for the span
- `options.params`: Additional parameters to log
- `fn`: The function to wrap

### OpenAI Integration

#### `wrapOpenAI(openAIClient, logger?)`

Wraps an OpenAI client to automatically log all chat completions.

```typescript
const openai = wrapOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }));
```

Parameters:
- `openAIClient`: The OpenAI client instance to wrap
- `logger` (optional): A custom GalileoLogger instance

### Workflow Management

#### GalileoLogger Class

The core class for managing traces and spans.

```typescript
import { GalileoLogger } from 'galileo';

const logger = new GalileoLogger({
  projectName: 'my-project',
  logStreamName: 'development'
});
```

##### Methods

###### `startTrace(input, output?, name?, createdAt?, durationNs?, userMetadata?, tags?)`

Starts a new trace.

```typescript
logger.startTrace('User query', undefined, 'user-interaction');
```

###### `addLlmSpan(options)`

Adds an LLM span to the current trace.

```typescript
logger.addLlmSpan({
  input: messages,
  output: response,
  model: 'gpt-4o',
  name: 'completion-generation'
});
```

###### `addRetrieverSpan(input, output, name?, durationNs?, createdAt?, userMetadata?, tags?, statusCode?)`

Adds a retriever span to the current trace.

```typescript
logger.addRetrieverSpan(
  'search query',
  retrievedDocuments,
  'document-retrieval'
);
```

###### `addToolSpan(input, output?, name?, durationNs?, createdAt?, userMetadata?, tags?, statusCode?, toolCallId?)`

Adds a tool span to the current trace.

```typescript
logger.addToolSpan(
  JSON.stringify(toolInput),
  JSON.stringify(toolOutput),
  'calculator-tool'
);
```

###### `addWorkflowSpan(input, output?, name?, durationNs?, createdAt?, userMetadata?, tags?)`

Adds a workflow span to the current trace.

```typescript
logger.addWorkflowSpan(
  'workflow input',
  undefined,
  'user-workflow'
);
```

###### `conclude(options)`

Concludes the current span or trace.

```typescript
logger.conclude({
  output: 'Final result',
  durationNs: performance.now() - startTime
});
```

### Utility Functions

#### Project Management

```typescript
import { getProjects, createProject, getProject } from 'galileo';

// Get all projects
const projects = await getProjects();

// Create a new project
const newProject = await createProject('My New Project');

// Get a specific project
const project = await getProject('My Project');
```

#### Log Stream Management

```typescript
import { getLogStreams, createLogStream, getLogStream } from 'galileo';

// Get all log streams for a project
const logStreams = await getLogStreams('My Project');

// Create a new log stream
const newLogStream = await createLogStream('My Project', 'production');

// Get a specific log stream
const logStream = await getLogStream('My Project', 'development');
```

#### Dataset Management

```typescript
import { getDatasets, createDataset, getDatasetContent, getDataset } from 'galileo';

// Get all datasets
const datasets = await getDatasets();

// Create a new dataset
const newDataset = await createDataset('My Dataset');

// Get dataset content
const content = await getDatasetContent('My Dataset');

// Get a specific dataset
const dataset = await getDataset('My Dataset');
```

## Use Cases

### Simple Chatbot

```typescript
import { init, flush, wrapOpenAI } from 'galileo';
import { OpenAI } from 'openai';
import dotenv from 'dotenv';

dotenv.config();

const openai = wrapOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }));

async function run() {
  // Initialize Galileo
  init({
    projectName: 'chatbot-project',
    logStreamName: 'development'
  });

  // Make an OpenAI request (automatically logged)
  const result = await openai.chat.completions.create({
    model: "gpt-4o",
    messages: [{ content: "Say hello world!", role: "user" }],
  });

  console.log(result.choices[0].message.content);

  // Flush logs before exiting
  await flush();
}

run().catch(console.error);
```

### RAG Applications

```typescript
import { log, init, flush, wrapOpenAI } from 'galileo';
import { OpenAI } from 'openai';

// Initialize Galileo
init({
  projectName: 'rag-project',
  logStreamName: 'development'
});

const openai = wrapOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }));

// Create a logged retriever function
const retrieveDocuments = log(
  { spanType: 'retriever' },
  async (query) => {
    // Implement your retrieval logic here
    return documents;
  }
);

// Main RAG function
async function rag(query) {
  // Retrieve documents (logged as a retriever span)
  const documents = await retrieveDocuments(query);
  
  // Format documents for the prompt
  const formattedDocs = documents.map((doc, i) => 
    `Document ${i+1}: ${doc.text}`
  ).join('\n\n');

  // Create the prompt
  const prompt = `
    Answer the following question based on the context provided:
    
    Question: ${query}
    
    Context:
    ${formattedDocs}
  `;

  // Generate response (automatically logged as an LLM span)
  const response = await openai.chat.completions.create({
    model: "gpt-4o",
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: prompt }
    ],
  });

  return response.choices[0].message.content;
}

// Example usage
async function main() {
  const answer = await rag("What is Galileo?");
  console.log(answer);
  
  // Flush logs before exiting
  await flush();
}

main().catch(console.error);
```

### Agent Systems

```typescript
import { log, init, flush, wrapOpenAI } from 'galileo';
import { OpenAI } from 'openai';

// Initialize Galileo
init({
  projectName: 'agent-project',
  logStreamName: 'development'
});

const client = wrapOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }));

// Define tools with logging
const calculator = log(
  { spanType: 'tool', name: 'calculator' },
  async (expression) => {
    try {
      const result = Function(`'use strict'; return (${expression})`)();
      return `The result of ${expression} is ${result}`;
    } catch (error) {
      return `Error calculating ${expression}: ${error.message}`;
    }
  }
);

// Main processing function with logging
const processQuery = log(
  { spanType: 'workflow' },
  async (query) => {
    // Initialize conversation
    const messages = [
      { role: "system", content: "You are a helpful assistant that can use tools." },
      { role: "user", content: query }
    ];
    
    // Define tools for the model
    const tools = [
      {
        type: "function",
        function: {
          name: "calculator",
          description: "Calculate the result of a mathematical expression",
          parameters: {
            type: "object",
            properties: {
              expression: {
                type: "string",
                description: "The mathematical expression to evaluate"
              }
            },
            required: ["expression"]
          }
        }
      }
    ];
    
    // Agent loop
    while (true) {
      // Get next action from LLM
      const response = await client.chat.completions.create({
        model: "gpt-4o",
        messages: messages,
        tools: tools,
      });
      
      const assistantMessage = response.choices[0].message;
      messages.push(assistantMessage);
      
      // Check if LLM is done
      if (!assistantMessage.tool_calls || assistantMessage.tool_calls.length === 0) {
        return assistantMessage.content;
      }
      
      // Process tool calls
      for (const toolCall of assistantMessage.tool_calls) {
        const functionName = toolCall.function.name;
        const functionArgs = JSON.parse(toolCall.function.arguments);
        
        // Execute the appropriate tool
        let result;
        if (functionName === "calculator") {
          result = await calculator(functionArgs.expression);
        } else {
          result = `Unknown tool: ${functionName}`;
        }
        
        // Add tool result to conversation
        messages.push({
          tool_call_id: toolCall.id,
          role: "tool",
          name: functionName,
          content: result
        });
      }
    }
  }
);

// Example usage
async function main() {
  const result = await processQuery("What is 123 * 456?");
  console.log(result);
  
  // Flush logs before exiting
  await flush();
}

main().catch(console.error);
```

## Advanced Features

### Custom Metadata

You can add custom metadata to spans for additional context:

```typescript
logger.addLlmSpan({
  input: messages,
  output: response,
  model: 'gpt-4o',
  metadata: {
    user_id: 'user-123',
    session_id: 'session-456',
    feature: 'product-search'
  }
});
```

### Tagging

Add tags to spans for easier filtering and analysis:

```typescript
logger.addToolSpan(
  toolInput,
  toolOutput,
  'search-tool',
  undefined,
  undefined,
  undefined,
  ['production', 'search-feature', 'v2']
);
```

### Performance Metrics

Track performance metrics for spans:

```typescript
const startTime = performance.now();
// ... perform operation
const endTime = performance.now();

logger.addLlmSpan({
  input: messages,
  output: response,
  model: 'gpt-4o',
  durationNs: (endTime - startTime) * 1000000, // Convert ms to ns
  numInputTokens: inputTokenCount,
  numOutputTokens: outputTokenCount,
  totalTokens: totalTokenCount
});
```

## Troubleshooting

### Common Issues

1. **Missing API Key**
   
   Ensure that the `GALILEO_API_KEY` environment variable is set or that you're providing the API key directly.

2. **Logs Not Appearing**
   
   Make sure you're calling `flush()` before your application exits to ensure all logs are sent to the Galileo platform.

3. **Incorrect Project or Log Stream Names**
   
   Verify that the project and log stream names you're using exist in your Galileo account.

### Debugging

Enable debug logging by setting the `GALILEO_DEBUG` environment variable:

```
GALILEO_DEBUG=true
```

This will output additional information about the SDK's operations to help diagnose issues.

## Conclusion

The Galileo SDK provides comprehensive tools for monitoring and debugging LLM applications. By integrating Galileo into your application, you can gain valuable insights into your AI system's performance, identify issues, and improve the quality of your AI-powered features.

For more information, visit the [Galileo website](https://www.rungalileo.io/) or contact support at support@rungalileo.io. 