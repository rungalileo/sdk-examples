# 📖 Galileo.ai SDK Examples
[![GitHub stars](https://img.shields.io/github/stars/Naereen/StrapDown.js.svg?style=social&label=Star&maxAge=2592000)](https://GitHub.com/Naereen/StrapDown.js/stargazers/) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) 
This repository contains example implementations and reference code for using the Galileo.ai SDK across both python and typescript applications. Galileo.ai is an evaluation platform for AI applications that helps you monitor, debug, and improve your LLM-powered applications.

➡️ Sign up for a free account on [Galileo.ai](https://app.galileo.ai/sign-up).

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
- **Datasets & Experiments**: Managing test data and running controlled experiments

## 🚢 Getting Started

Each directory contains standalone examples with their own setup instructions and dependencies. Generally, you'll need to:

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




