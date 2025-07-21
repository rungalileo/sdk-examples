# Galileo TypeScript RAG

This is a TypeScript implementation of a Retrieval-Augmented Generation (RAG) system that uses Galileo for logging. The system retrieves relevant documents based on a query and uses them to generate an answer.

## Features

- Simulated document retrieval (can be replaced with actual vector database retrieval)
- LLM-based answer generation using retrieved documents
- Galileo logging for retriever and LLM spans
- Interactive command-line interface

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
# Galileo Environment Variables
GALILEO_API_KEY=your-galileo-api-key             # Your Galileo API key.
GALILEO_PROJECT=your-galileo-project-name        # Your Galileo project name.
GALILEO_LOG_STREAM=your-galileo-log-stream       # The name of the log stream you want to use for logging.

# Provide the console url below if you are using a custom deployment, and not using app.galileo.ai
# GALILEO_CONSOLE_URL=your-galileo-console-url   # Optional if you are using a hosted version of Galileo

OPENAI_API_KEY=your_openai_api_key_here
```

## Running the RAG System

To run the RAG system:

```bash
npm start
```

Or with TypeScript directly:

```bash
npx ts-node app.ts
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

1. The system uses the `@log` decorator from Galileo to log retriever and LLM spans.
2. When a query is received, the system:
   - Retrieves relevant documents (currently simulated)
   - Formats the documents into a prompt
   - Sends the prompt to the LLM to generate an answer
   - Returns the answer to the user
3. The entire process is logged in Galileo for observability.

## Span Hierarchy

The span hierarchy created by the RAG system looks like:

- `retrieveDocuments` (retriever span)
- LLM call (automatically logged by the wrapped OpenAI client)

This hierarchy accurately represents the flow of operations in the RAG system.

## Extending the System

To extend this system with a real vector database:

1. Add a vector database client (e.g., Pinecone, Weaviate, Chroma) to the dependencies
2. Modify the `retrieveDocuments` function to query the vector database
3. Add document embedding and indexing functionality 