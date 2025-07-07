# 🤝 Contributing to Galileo.ai SDK Examples

Thank you for your interest in contributing to the Galileo.ai SDK Examples repository! This guide will help you understand how to contribute effectively and maintain the quality of our examples.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Adding New Examples](#adding-new-examples)
- [Code Standards](#code-standards)
- [Documentation Guidelines](#documentation-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Example Categories](#example-categories)

## 🚀 Getting Started

### Prerequisites

1. **Galileo.ai Account**: You'll need a free account on [Galileo.ai](https://app.galileo.ai/sign-up)
2. **API Key**: Obtain your API key from the [Galileo.ai dashboard](https://app.galileo.ai/settings/api-keys)
3. **Development Environment**: 
   - For Python examples: Python 3.8+ and pip
   - For TypeScript examples: Node.js 16+ and npm/yarn

### Setup

1. Fork this repository
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/sdk-examples.git
   cd sdk-examples
   ```
3. Create a new branch for your contribution:
   ```bash
   git checkout -b feature/your-example-name
   ```

## 🏗️ Project Structure

Our repository follows a clear structure to maintain organization:

```
sdk-examples/
├── python/                    # Python examples
│   ├── agent/                 # Agent implementations
│   ├── chatbot/               # Chatbot examples
│   ├── rag/                   # RAG applications
│   └── dataset-experiments/   # Dataset management
├── typescript/                # TypeScript examples
│   ├── agent/                 # Agent implementations
│   ├── chatbot/               # Chatbot examples
│   ├── rag/                   # RAG applications
│   └── datasets-experiments/  # Dataset management
└── README.md                  # Main documentation
```

## ➕ Adding New Examples

### 1. Choose Your Category

Examples should fit into one of these categories:
- **Agent**: LLM systems that use tools and make decisions
- **Chatbot**: Simple conversational applications
- **RAG**: Retrieval-Augmented Generation applications
- **Dataset & Experiments**: Data management and testing

### 2. Create Your Example Directory

Create a new directory following this naming convention:
- Use kebab-case: `my-awesome-example`
- Be descriptive but concise
- Place in the appropriate language folder (`python/` or `typescript/`)

### 3. Required Files

Every example should include:

#### For Python Examples:
```
your-example/
├── README.md              # Documentation and setup instructions
├── requirements.txt       # Python dependencies
├── main.py               # Main application file
├── .env.example          # Environment variables template
└── (optional) tests/     # Test files
```

#### For TypeScript Examples:
```
your-example/
├── README.md              # Documentation and setup instructions
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── index.ts               # Main application file
├── .env.example           # Environment variables template
└── (optional) tests/      # Test files
```

### 4. Example README.md Template

```markdown
# Example Name

Brief description of what this example demonstrates.

## 🎯 What This Example Shows

- Key feature 1
- Key feature 2
- Key feature 3

## 🚀 Quick Start

1. Install dependencies:
   ```bash
   # For Python
   pip install -r requirements.txt
   
   # For TypeScript
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Galileo API key
   ```

3. Run the example:
   ```bash
   # For Python
   python main.py
   
   # For TypeScript
   npm start
   ```

## 🔧 Configuration

Explain any configuration options or settings.

## 📚 Learn More

- [Galileo.ai Documentation](https://v2docs.galileo.ai/)
- [Any Related Example Link](/path/to/related/example)
```

## 📝 Code Standards

### Python Standards

- **Python Version**: Target Python 3.8+
- **Code Style**: Follow PEP 8 guidelines
- **Dependencies**: Use `requirements.txt` 
- **Type Hints**: Include type hints for function parameters and return values
- **Docstrings**: Add docstrings to functions and classes

```python
from typing import List, Optional
from galileo import Galileo

def process_data(data: List[str], config: Optional[dict] = None) -> dict:
    """
    Process the input data with Galileo integration.
    
    Args:
        data: List of strings to process
        config: Optional configuration dictionary
        
    Returns:
        Dictionary containing processed results
    """
    # Your code here
    pass
```

### TypeScript Standards

- **Node.js Version**: Target Node.js 16+
- **Code Style**: Use ESLint and Prettier
- **Dependencies**: Use `package.json` 
- **TypeScript**: Use strict mode and proper typing
- **Comments**: Add JSDoc comments for functions

```typescript
import { Galileo } from 'galileo';

interface ProcessConfig {
  enabled: boolean;
  timeout?: number;
}

/**
 * Process the input data with Galileo integration
 * @param data - Array of strings to process
 * @param config - Optional configuration object
 * @returns Promise resolving to processed results
 */
async function processData(
  data: string[], 
  config?: ProcessConfig
): Promise<Record<string, any>> {
  // Your code here
}
```

### Galileo Integration Standards

- **API Key**: Always use environment variables for API keys
- **Error Handling**: Implement proper error handling for Galileo API calls
- **Logging**: Use Galileo's logging features appropriately
- **Documentation**: Explain how Galileo is being used in your example

```python
import os
from galileo import Galileo

# Initialize Galileo with API key from environment
galileo = Galileo(api_key=os.getenv("GALILEO_API_KEY"))

# Use Galileo for tracing and monitoring
with galileo.trace("my-operation") as trace:
    # Your LLM operations here
    result = llm.generate("Your prompt")
    trace.log("result", result)
```

## 📚 Documentation Guidelines

### README Requirements

Every example must have a README.md that includes:

1. **Clear Title and Description**
2. **What the Example Demonstrates** - List key features
3. **Quick Start Instructions** - Step-by-step setup
4. **Configuration Details** - Environment variables, settings
5. **Expected Output** - What users should see
6. **Troubleshooting** - Common issues and solutions
7. **Learn More** - Links to relevant documentation

### Code Comments

- Comment complex logic
- Explain Galileo-specific code
- Add inline comments for non-obvious operations
- Use docstrings for functions and classes

## 🧪 Testing Guidelines

### Test Requirements

- **Basic Functionality**: Ensure the example runs without errors
- **Galileo Integration**: Verify Galileo features work correctly
- **Error Handling**: Test error scenarios
- **Documentation**: Verify README instructions work

### Test Structure

```
your-example/
├── tests/
│   ├── test_main.py          # Main functionality tests
│   ├── test_galileo.py       # Galileo integration tests
│   └── conftest.py           # Test configuration
```

### Running Tests

```bash
# Python
python -m pytest tests/

# TypeScript
npm test
```

## 🔄 Pull Request Process

### Before Submitting

1. **Test Your Example**: Ensure it runs correctly
2. **Update Documentation**: Verify README is complete and accurate
3. **Check Dependencies**: Ensure all dependencies are properly listed
4. **Environment Variables**: Provide `.env.example` file
5. **Code Review**: Self-review your code for quality

### PR Checklist

- [ ] Example runs successfully
- [ ] README.md is complete and accurate
- [ ] Dependencies are properly listed
- [ ] Environment variables are documented
- [ ] Code follows style guidelines
- [ ] Galileo integration is properly implemented
- [ ] Tests pass (if applicable)
- [ ] No sensitive data is included

### PR Description Template

```markdown
## Description
Brief description of what this example demonstrates.

## Type of Example
- [ ] Agent
- [ ] Chatbot
- [ ] RAG
- [ ] Dataset & Experiments

## Language
- [ ] Python
- [ ] TypeScript

## Key Features
- Feature 1
- Feature 2
- Feature 3

## Testing
- [ ] Example runs successfully
- [ ] README instructions work
- [ ] Galileo integration tested

## Screenshots/Demo
(If applicable)
```

## 🎯 Example Categories

### Agent Examples

Agent examples should demonstrate:
- Tool usage and decision-making
- Multi-step workflows
- Error handling and recovery
- Galileo's agent monitoring features

**Good Examples:**
- Weather agent with multiple tools
- Financial services agent with document processing
- Customer support agent with knowledge base

### Chatbot Examples

Chatbot examples should show:
- Conversation management
- Context handling
- Response generation
- Galileo's conversation tracking

**Good Examples:**
- Simple Q&A chatbot
- Context-aware conversations
- Multi-turn dialogue systems

### RAG Examples

RAG examples should demonstrate:
- Document retrieval
- Context augmentation
- Source attribution
- Galileo's RAG monitoring

**Good Examples:**
- Document Q&A systems
- Knowledge base chatbots
- Research assistants

### Dataset & Experiment Examples

Dataset examples should show:
- Data management
- Experiment tracking
- Evaluation metrics
- Galileo's dataset features

**Good Examples:**
- A/B testing frameworks
- Evaluation pipelines
- Data versioning

## 🆘 Getting Help

- **Issues**: Use GitHub Issues for bugs or feature requests
- **Documentation**: Check the [Galileo.ai docs](https://v2docs.galileo.ai/)
- **Version Control**: use Git for version control and submit a PR when you are ready for review. Tag @jimbobbennett, @erinmikailstaples or @rschwabco for code review. 


---

Thank you for contributing to the Galileo.ai SDK Examples! 

Your examples help the community learn and build better AI applications. 🚀 