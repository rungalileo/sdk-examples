# 📖 Galileo.ai SDK Examples

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Last Updated](https://img.shields.io/github/last-commit/rungalileo/sdk-examples?style=flat-square&label=Last%20Updated&color=blue)](https://github.com/rungalileo/sdk-examples/commits/main)
[![Examples](https://img.shields.io/badge/Examples-40+-orange.svg?style=flat-square)](#-repository-structure)

This repository contains example implementations and reference code for using the Galileo.ai SDK across both Python and TypeScript applications. Galileo helps folks build reliable AI applications across a multitude of tech stacks.

**➡️ Sign up for a free account on [Galileo.ai](https://app.galileo.ai/sign-up).**

## 🍳 Cookbooks & Tutorials

For comprehensive guides and step-by-step tutorials, check out our **[Galileo Cookbooks](https://v2docs.galileo.ai/cookbooks/overview)** featuring:

- **Agent Development** - Multi-agent systems, LangGraph workflows, and OpenTelemetry integration
- **RAG Applications** - MongoDB Atlas, Elasticsearch, and vector search implementations
- **Custom Metrics** - Domain-specific evaluations and LLM-as-a-Judge patterns
- **Production Monitoring** - Observability, tracing, and reliability patterns

---

## 📋 Table of Contents

### Sample projects

When you first sign up for Galileo, you will get 2 sample projects created, a simple chatbot, and a multi-agent banking chatbot. The code for these projects is in this repo.

You can read more about these in our [Get started with sample projects documentation](https://v2docs.galileo.ai/getting-started/sample-projects/sample-projects).

#### Python
  - [Simple chatbot using OpenAI/Ollama](/python/chatbot/sample-project-chatbot/openai-ollama/) - Simple chatbot using the OpenAI SDK to interact with OpenAI or Ollama
  - [Simple chatbot using Anthropic](/python/chatbot/sample-project-chatbot/anthropic/) - Simple chatbot using the Anthropic SDK
  - [Simple chatbot using Azure AI Inference](/python/chatbot/sample-project-chatbot/azure-inference/) - Simple chatbot using the Azure AI Inference SDK to interact with models deployed to Azure AI Foundry

#### Typescript
  - [Simple chatbot using OpenAI/Ollama](/typescript/chatbot/sample-project-chatbot/openai-ollama/) - Simple chatbot using the OpenAI SDK to interact with OpenAI or Ollama
  - [Simple chatbot using Anthropic](/typescript/chatbot/sample-project-chatbot/anthropic/) - Simple chatbot using the Anthropic SDK
  - [Simple chatbot using Azure AI Inference](/typescript/chatbot/sample-project-chatbot/azure-inference/) - Simple chatbot using the Azure AI Inference SDK to interact with models deployed to Azure AI Foundry

### 🤖 Agent Examples

#### Python Agents 🐍
- **[LangChain Agent](/python/agent/langchain-agent/)** - Basic LangChain agent with Galileo integration
- **[LangGraph FSI Agent](/python/agent/langgraph-fsi-agent/)** - Financial services agent with before/after implementations  
- **[LangGraph + OpenTelemetry](/python/agent/langgraph-otel/)** - 🎆 **Featured** - Comprehensive observability with OpenTelemetry and Galileo
- **[CrewAI Agent](/python/agent/crew-ai/)** - Multi-agent collaboration using CrewAI framework
- **[Startup Simulator 3000](/python/agent/startup-simulator-3000/)** - Advanced agent with startup business simulation
- **[Weather Vibes Agent](/python/agent/weather-vibes-agent/)** - Multi-function agent for weather, recommendations, and YouTube videos
- **[Minimal Agent Example](/python/agent/minimal-agent-example/)** - Simple agent with basic tool usage

#### TypeScript Agents 📜  
- **[LangGraph FSI Agent](/typescript/agent/langgraph-fsi-agent/)** - Financial services agent in TypeScript
- **[Stripe Agent Tool](/typescript/agent/stripe-agent-tool/)** - 💳 Agent with Stripe payment processing integration
- **[Mastra Template CSV to Questions](/typescript/agent/mastra-template-csv-to-questions/)** - Galileo tracing with Mastra framework and OpenInference
- **[Minimal Agent Example](/typescript/agent/minimal-agent-example/)** - Basic TypeScript agent implementation

### 💬 Chatbot Examples

#### Python Chatbots 🐍
- **[Basic Examples](/python/chatbot/basic-examples/)** - Simple conversational application with context management
- **[Sample Project Chatbot](/python/chatbot/sample-project-chatbot/)** - Multi-LLM chatbot with experiment capabilities:
  - [OpenAI/Ollama variant](/python/chatbot/sample-project-chatbot/openai-ollama/) 
  - [Anthropic variant](/python/chatbot/sample-project-chatbot/anthropic/)
  - [Azure AI Inference variant](/python/chatbot/sample-project-chatbot/azure-inference/)

#### TypeScript Chatbots 📜
- **[Basic Examples](/typescript/chatbot/basic-examples/)** - Fundamental chatbot patterns in TypeScript  
- **[Sample Project Chatbot](/typescript/chatbot/sample-project-chatbot/)** - Multi-LLM chatbot implementations:
  - [OpenAI/Ollama variant](/typescript/chatbot/sample-project-chatbot/openai-ollama/)
  - [Anthropic variant](/typescript/chatbot/sample-project-chatbot/anthropic/)
  - [Azure AI Inference variant](/typescript/chatbot/sample-project-chatbot/azure-inference/)

### 🔍 RAG (Retrieval-Augmented Generation) Examples

#### Python RAG 🐍
- **[CLI RAG Demo](/python/rag/cli-rag-demo/)** - Command-line RAG with chunk utilization challenges
- **[Elastic Chatbot RAG App](/python/rag/elastic-chatbot-rag-app/)** - Full-stack RAG application with Elasticsearch
- **[Healthcare Support Portal](/python/rag/healthcare-support-portal/)** - Domain-specific RAG for healthcare queries

#### TypeScript RAG 📜
- **[Basic RAG Implementation](/typescript/rag/)** - Fundamental RAG patterns in TypeScript

### 📊 Dataset & Experiment Examples

#### Python Datasets 🐍
- **[Dataset Experiments](/python/dataset-experiments/)** - Managing test data and running controlled experiments

#### TypeScript Datasets 📜
- **[Dataset Experiments](/typescript/datasets-experiments/)** - Dataset management and experimentation in TypeScript

#### 📚 Additional Resources

- [Galileo SDK Documentation](https://v2docs.galileo.ai/sdk-api/overview) - SDK documentation
- [Galileo API Reference](https://v2docs.galileo.ai/api-reference/health/healthcheck) - TypeScript SDK package
- [Galileo Release Notes](https://v2docs.galileo.ai/release-notes)

## 📖 Read the Docs

### Core Documentation
- **[Galileo.ai Documentation](https://v2docs.galileo.ai/what-is-galileo)** - Complete platform overview
- **[Galileo Cookbooks](https://v2docs.galileo.ai/cookbooks/overview)** - 🔥 **Step-by-step tutorials and guides**
- **[Python SDK Documentation](https://v2docs.galileo.ai/sdk-api/python/overview)** - Python SDK reference
- **[TypeScript SDK Documentation](https://v2docs.galileo.ai/sdk-api/typescript/overview)** - TypeScript SDK reference
- **[API Reference](https://v2docs.galileo.ai/api-reference/health/healthcheck)** - REST API documentation
- **[Release Notes](https://v2docs.galileo.ai/release-notes)** - Latest updates and features

## 📦 Requirements

- A free account on [Galileo.ai](https://app.galileo.ai/sign-up)
- A free Galileo API key (found in the [Galileo.ai dashboard](https://app.galileo.ai/settings/api-keys))

## 🎆 Key Features & Use Cases

### 🚀 What You'll Learn
- **Agent Development** - Build AI systems that can use tools, make decisions, and collaborate
- **Observability** - Comprehensive tracing with OpenTelemetry and Galileo integration  
- **RAG Applications** - Combine knowledge bases with LLMs for enhanced responses
- **Multi-LLM Support** - Work with OpenAI, Anthropic, Azure, and local models like Ollama
- **Production Patterns** - Error handling, evaluation, and monitoring best practices

### 🎯 Application Patterns Covered
- **🤖 AI Agents** - Tool-using systems with decision-making capabilities
  - *Featured: LangGraph + OpenTelemetry* - Complete observability setup
  - *Stripe Agent* - Payment processing integration
  - *Weather Vibes* - Multi-function agent with external APIs
- **💬 Chatbots** - Conversational applications with context management
- **🔍 RAG Systems** - Knowledge retrieval and generation pipelines
- **📊 Data & Experiments** - Testing, evaluation, and dataset management

## 🚢 Get Started

Each directory contains standalone examples with their own setup instructions and dependencies.

1. Create a free account on [Galileo.ai](https://app.galileo.ai/sign-up) and obtain an API key
2. Install the Galileo SDK for your language of choice
3. Clone this repository
4. Navigate to the example you want to run
5. Install dependencies
6. Run the example

## 🤝 Contributing

Have a great example of how to use Galileo? Or rather — have something you'd like to see how it works with Galileo?
 Please see our [Contributing Guide](CONTRIBUTING.md) for detailed information on how to:

- Open an issue to discuss your idea
- Add new examples
- Follow our coding standards
- Submit pull requests
- Test your contributions

## 🗺️ Repository Structure

```tree
sdk-examples/
├── python/                    # 🐍 Python Examples (20+ projects)
│   ├── agent/                 # AI Agents with tool usage
│   │   ├── langchain-agent/
│   │   ├── langgraph-fsi-agent/
│   │   ├── langgraph-otel/    # ⭐ Featured: OpenTelemetry integration
│   │   ├── crew-ai/
│   │   ├── startup-simulator-3000/
│   │   ├── weather-vibes-agent/
│   │   └── minimal-agent-example/
│   ├── chatbot/               # Conversational AI applications
│   │   ├── basic-examples/
│   │   └── sample-project-chatbot/
│   │       ├── openai-ollama/
│   │       ├── anthropic/
│   │       └── azure-inference/
│   ├── rag/                   # Retrieval-Augmented Generation
│   │   ├── cli-rag-demo/
│   │   ├── elastic-chatbot-rag-app/
│   │   └── healthcare-support-portal/
│   └── dataset-experiments/   # Data management and testing
│
├── typescript/                # 📜 TypeScript Examples (15+ projects)
│   ├── agent/                 # AI Agents in TypeScript
│   │   ├── langgraph-fsi-agent/
│   │   ├── stripe-agent-tool/  # 💳 Payment processing
│   │   ├── mastra-template-csv-to-questions/
│   │   └── minimal-agent-example/
│   ├── chatbot/               # TypeScript chatbots
│   │   ├── basic-examples/
│   │   └── sample-project-chatbot/
│   │       ├── openai-ollama/
│   │       ├── anthropic/
│   │       └── azure-inference/
│   ├── rag/                   # RAG implementations
│   └── datasets-experiments/  # Dataset management
│
└── .github/                   # GitHub templates and CI/CD
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
