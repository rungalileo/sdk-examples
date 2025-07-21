# 🌦️ Weather Vibes Agent Tutorial Overview

Welcome to the Weather Vibes Agent tutorial! This guide will walk you through building and understanding an AI agent that provides weather information, clothing recommendations, and matching YouTube videos based on the current weather in a location - all while using Galileo.ai to monitor and improve your agent's performance.

## 🎒 What You'll Need

Before we dive into the code ocean, make sure you've packed:

- **Python 3.8+** installed on your system
- **API Keys** (free options available):
  - OpenAI API key (for agent reasoning)
  - WeatherAPI key (for weather data)
  - YouTube API key (for video recommendations)
  - Galileo API key (for monitoring and evaluation)
- **Development Environment**:
  - Code editor of choice
  - Terminal/command-line access
  - Git (to clone the repository)
- **Package Manager**:
  - [uv](https://docs.astral.sh/uv/getting-started/installation/) (will be used to create the virtual environment and install dependencies)

## 🧠 Helpful Background Knowledge
Don't worry if you're not an expert in all these areas - the tutorial is designed to guide you through each step without any prior knowledge, and the code is well-documented.

- **Python Basics**: Functions, async/await, and error handling
- **API Knowledge**: RESTful APIs and how to use keys
- **LLM Concepts**: Understanding of AI agents and large language models
- **Terminal Skills**: Basic command-line comfort

## What You'll Learn
By completing this tutorial, you will:

1. **Build a Multi-Function AI Agent**: Create an agent that combines multiple tools and APIs
2. **Implement API Integrations**:
   - Weather data retrieval from WeatherAPI
   - Video recommendations from YouTube
   - AI-based recommendations using OpenAI
3. **Use Galileo for Agent Evaluation**:
   - Instrument your agent with Galileo SDK
   - Track agent performance through traces
   - Analyze execution flow and identify bottlenecks
   - Collect and evaluate agent outputs
4. **Create Agent Interfaces**:
   - Command-line interface for testing
   - Web API for integration with other systems
5. **Follow Best Practices**:
   - Structured agent architecture
   - Error handling and graceful failure
   - Configuration management
   - Code organization and modularity

1. **Observe Your AI in Action**: See exactly what your agent is doing at each step
   - Track every API call with precise timing
   - Understand execution flow through hierarchical traces
   - Identify performance bottlenecks in real-time

2. **Learn to use the Galileo Python SDK**:
   - Use the `log` decorator to instrument functions
   - Create spans for different operation types (LLM, tool usage, workflows)
   - Set up context management with `galileo_context`
   - Capture inputs and outputs across your entire agent
   - Add metadata for richer analysis

3. **Debug Like a Pro**:
   - Pinpoint exactly where errors occur
   - Understand the full context of failures
   - Compare successful vs. unsuccessful runs
   - Analyze performance patterns across multiple executions

4. **Build a Robust Agent Architecture**:
   - Combine weather data, recommendations, and video suggestions
   - Handle errors gracefully at every step
   - Structure your code for maintainability and clarity
   - See how proper instrumentation makes complex agents manageable

5. **Level Up Your Dev Skills**:
   - Apply best practices for async Python
   - Structure complex workflows with clear separation of concerns
   - Implement professional-grade error handling and reporting
   - Use environment variables for secure configuration management

## 🎉 Let's Get Started

1. **Clone the Code**:
   ```bash
   git clone https://github.com/rungalileo/sdk-examples.git
   cd sdk-examples/python/agent/weather-vibes-agent
   ```

2. **Set Up Your Environment**:
   ```bash
   # Create a virtual environment
   uv venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install deps with uv
   uv install -r requirements.txt
   ```

3. **Configure Your API Keys**:
   Create a `.env` file in the project root:

   ```
    # Galileo Environment Variables
    GALILEO_API_KEY=your-galileo-api-key             # Your Galileo API key.
    GALILEO_PROJECT=your-galileo-project-name        # Your Galileo project name.
    GALILEO_LOG_STREAM=weather_vibes_agent
    
    # Provide the console url below if you are using a custom deployment, and not using app.galileo.ai
    # GALILEO_CONSOLE_URL=your-galileo-console-url   # Optional if you are using a hosted version of Galileo
    
   OPENAI_API_KEY=your_openai_key
   WEATHERAPI_KEY=your_weatherapi_key
   YOUTUBE_API_KEY=your_youtube_key
   ```

4. **Follow the Tutorial Sections**:
   - 01-weather-vibes-overview.md (this file)
   - 02-installation-instructions.md
   - 03-using-galileo.md

6. **Run the Weather Vibes App**:
   ```bash
   # Get the weather vibe for Tokyo
   python agent.py "Tokyo"
   
   # Get fancy with options
   python agent.py --location "New York" --units imperial --mood relaxing --verbose
   ```

## 🔍 What to Watch in the Galileo Dashboard

After running your agent, head over to your Galileo dashboard to see:

1. **Complete Trace Hierarchy**: Visualize how your agent's components interact
2. **Timing Breakdown**: See exactly how long each operation takes
3. **Input/Output Analysis**: Explore what data flows between components
4. **Error Insights**: If something goes wrong, see exactly where and why

## 🗂️ Project Architecture

- **agent.py**: Our main agent with Galileo instrumentation
- **agent/weather_vibes_agent.py**: The core agent implementation
- **tools/**: The specialized tools our agent uses
  - **weather_tool.py**: For fetching weather data
  - **recommendation_tool.py**: For suggesting items based on weather
  - **youtube_tool.py**: For finding weather-appropriate videos
- **templates/**: Web interface templates (if you're feeling fancy)

Ready to build something awesome while learning how to monitor it like a pro? Let's rock this! 🌈✨

Happy building!
