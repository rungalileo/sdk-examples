# How to use CrewAI Planning in your Crew of agents

The planning feature in CrewAI allows you to add planning capability to your crew. When enabled, before each Crew iteration, all Crew information is sent to an AgentPlanner that will plan the tasks step by step, and this plan will be added to each task description.

This guide will serve as a demonstration of how to use the **planning** feature in your crews.

## Install dependencies

This project uses UV for Python dependency management. UV is a fast Python package and project manager that replaces pip, pip-tools, pipx, poetry, pyenv, virtualenv, and more.

### Install UV (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on macOS with Homebrew:
```bash
brew install uv
```

### Install project dependencies

```bash
# Install all dependencies
uv sync

# Or install with dev dependencies
uv sync --all-groups
```

### Running the application

Use `uv run` to execute Python scripts:

```bash
uv run python main.py
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
uv run python main.py
```

Or with specific arguments:

```bash
# Research a specific topic
uv run python main.py "AI trends in 2025"

# Specify date context
uv run python main.py "Quantum computing breakthroughs" --date "December 1, 2025"

# Clear todo list before starting
uv run python main.py "LLM reasoning" --clear-todos
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
