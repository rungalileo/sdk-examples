# How to use CrewAI Planning in your Crew of agents

The planning feature in CrewAI allows you to add planning capability to your crew. When enabled, before each Crew iteration, all Crew information is sent to an AgentPlanner that will plan the tasks step by step, and this plan will be added to each task description.

This guide will serve as a demonstration of how to use the **planning** feature in your crews.

## Install dependencies

Install the required packages:

```bash
uv pip install -U crewai crewai-tools exa_py galileo
uv pip install --upgrade ipywidgets
```

Or use the requirements.txt file:

```bash
pip install -r requirements.txt
```

## Configure API keys

Configure API keys for both the LLM and Exa for searching the web. Create a `.env` file in the parent directory with:

```
OPENAI_API_KEY=your_openai_api_key
EXA_API_KEY=your_exa_api_key
```

See `.env.example` for reference.

## Usage

Run the research agent:

```bash
python main.py
```

The crew will:
1. Use the **Analyst** agent to do research
2. Use the **Reporter** agent to generate a detailed report from the research
3. Enable **planning** capabilities with `planning=True` before agents perform tasks
4. Use the specified `planning_llm` to plan the tasks

## Features

- **Planning**: Automatically plans tasks step by step before execution
- **Reasoning**: Agents can reason through problems with configurable attempts
- **Custom Tools**: Includes a TodoListTool for task management
- **Async Execution**: Supports asynchronous task execution
- **Web Search**: Uses Exa for web search capabilities

## Conclusion

The Planning feature is an alternative to the **Reasoning** feature in CrewAI. There's a good chance both perform similar or the reasoning will be better. We recommend trying both to see what works best for you.

For more information on Planning, please reference the [CrewAI documentation](https://docs.crewai.com/en/concepts/planning).

Happy building! 🎉
