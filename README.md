# 📖 Galileo.ai SDK Examples
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) 

This repository contains example implementations and reference code for using the Galileo.ai SDK across both Python and TypeScript applications. Galileo helps folks build reliable AI applications across a multitude of tech stacks.

**➡️ Sign up for a free account on [Galileo.ai](https://app.galileo.ai/sign-up).**

## 📋 Table of Contents

### 🤖 Agent Examples
- **[Python Agents](/python/agent/)**
  - [LangChain Agent](/python/agent/langchain-agent/) - Basic LangChain agent with Galileo integration
  - [LangGraph FSI Agent](/python/agent/langgraph-fsi-agent/) - Financial services agent with before/after implementations
  - [Minimal Agent Example](/python/agent/minimal-agent-example/) - Simple agent with basic tool usage
  - [Weather Vibes Agent](/python/agent/weather-vibes-agent/) - Multi-function agent for weather, recommendations, and YouTube videos
- **[TypeScript Agents](/typescript/agent/)**
  - [Minimal Agent](/typescript/agent/) - Basic TypeScript agent implementation

### 💬 Chatbot Examples
- **[Python Chatbot](/python/chatbot/)** - Simple conversational application with context management
- **[TypeScript Chatbot](/typescript/chatbot/)** - Basic chatbot implementation in TypeScript

### 🔍 RAG (Retrieval-Augmented Generation) Examples
- **[Python RAG](/python/rag/)**
  - [CLI RAG Demo](/python/rag/cli-rag-demo/) - Command-line RAG with chunk utilization challenges
  - [Elastic Chatbot RAG App](/python/rag/elastic-chatbot-rag-app/) - Full-stack RAG application with Elasticsearch
- **[TypeScript RAG](/typescript/rag/)** - Basic RAG implementation in TypeScript

### 📊 Dataset & Experiment Examples
- **[Python Datasets](/python/dataset-experiments/)** - Managing test data and running controlled experiments
- **[TypeScript Datasets](/typescript/datasets-experiments/)** - Dataset management in TypeScript

### 📚 Additional Resources
- [Galileo SDK Documentation](/typescript/galileo-sdk-documentation.md) - Comprehensive SDK documentation
- [Galileo SDK Package](/typescript/galileo-1.4.0.tgz) - TypeScript SDK package

## 📖 Read the Docs
- [Galileo.ai Documentation](https://v2docs.galileo.ai/what-is-galileo)
- [Galileo.ai Python SDK Documentation](https://v2docs.galileo.ai/sdk-api/python/overview)
- [Galileo.ai TypeScript SDK Documentation](https://v2docs.galileo.ai/sdk-api/typescript/overview)

## 📦 Requirements
- A free account on [Galileo.ai](https://app.galileo.ai/sign-up)
- A free Galileo API key (found in the [Galileo.ai dashboard](https://app.galileo.ai/settings/api-keys))

## 🍎 Use Cases
The examples cover several common LLM application patterns:
- **Chatbots**: Simple conversational applications
- **RAG**: Retrieval-Augmented Generation applications that combine knowledge bases with LLMs
- **Agents**: Systems where LLMs use tools and make decisions
  - *Weather Vibes Agent*: A multi-function agent that provides weather info, recommendations, and matching YouTube videos
- **Datasets & Experiments**: Managing test data and running controlled experiments

## 🚢 Getting Started
Each directory contains standalone examples with their own setup instructions and dependencies.

1. Create a free account on [Galileo.ai](https://app.galileo.ai/sign-up) and obtain an API key
2. Install the Galileo SDK for your language of choice
3. Clone this repository
4. Navigate to the example you want to run
5. Install dependencies
6. Run the example

## 🗺️ Repository Structure

``` 
sdk-examples/
├── typescript/         # TypeScript implementation examples
│   ├── agent/          # Agent implementation using Galileo SDK
│   ├── chatbot/        # Simple chatbot example
│   ├── datasets-experiments/ # Dataset and experiment examples
│   └── rag/            # Retrieval-Augmented Generation examples
│
├── python/             # Python implementation examples
│   ├── agent/          # Agent implementation using Galileo SDK
│   ├── chatbot/        # Simple chatbot example
│   ├── dataset-experiments/ # Dataset and experiment examples
│   └── rag/            # Retrieval-Augmented Generation examples
```

## TypeScript Examples

The TypeScript examples demonstrate how to integrate Galileo.ai into your Node.js/TypeScript applications. The SDK provides tools for:

- Tracing LLM interactions
- Monitoring retrieval operations in RAG applications
- Tracking agent tool usage and workflows
- Evaluating model outputs

### Setup

```bash
npm install galileo
```

## Python Examples

The Python examples show how to use the Galileo.ai Python SDK in your applications, covering similar use cases as the TypeScript examples.

### Setup

```bash
pip install galileo
```




