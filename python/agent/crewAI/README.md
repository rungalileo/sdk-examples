# CrewAI and Galileo Cookbook

This repository demonstrates how to build and run a small research crew using crewAI and how to instrument the application with Galileo for observability and evaluation engineering.

Below you'll find concise setup steps, configuration notes, and a short primer on Galileo so you know why we add it and what it provides.

## Resources

- [Add Galileo to CrewAI](https://v2docs.galileo.ai/how-to-guides/third-party-integrations/add-galileo-to-crewai/add-galileo-to-crewai)
- [crewAI first-crew guide](https://docs.crewai.com/en/guides/crews/first-crew)

## What is Galileo?

[Galileo](https://galileo.ai) is an observability and evaluation platform for generative AI agents. Integrating Galileo into a CrewAI project gives you:

- Structured logging of prompts, agent decisions, and model responses. 
- Metrics, logs, and traces to evaluate agent performance and behavior over time.
- A centralized dashboard for debugging, auditing, and running evaluations on AI agents. 

## Why add Galileo here?

- Faster troubleshooting: quickly find which agent produced what output and why
- Better evaluation: collect examples, compare model versions, and compute metrics
- Reproducibility: attach metadata (env, model, prompt) to recorded runs for later analysis

## Prerequisites

- Python 3.10–3.13
- `uv` tool available (this project uses `uv` for environment management and tooling)
- A [Galileo API key](https://app.galileo.ai/)
- A [Serper API Key](https://serper.dev/)
- An [OpenAI Key](https://platform.openai.com/))

## Quick setup

Run these steps from the repository root (`/Users/anais/galileo_quickstarts/crewai/research_crew`). Commands assume macOS + zsh.

1. Clone and open the repo

```zsh
git clone <repo-url>
cd /path/to/research_crew
```

2. Copy the .env.example and configure credentials

```zsh
cp .env.example .env
```

3. Install crewAI tool (via `uv`) if not already installed

```zsh
uv tool install crewai
uv tool list
```

4. Activate the project virtual environment

```zsh
source .venv/bin/activate
```

5. Install dependencies (recommended: target the active/project env)

Option A — use `uv` to install into the active environment (recommended when using `uv` workflows):

```zsh
# with .venv activated
uv pip install --active galileo python-dotenv
```

Option B — use the venv's pip directly:

```zsh
python -m pip install --upgrade pip
python -m pip install galileo python-dotenv
```

Both approaches ensure the interpreter used by `uv run` / `crewai run` has the packages available.

6. Verify the installation

```zsh
python -c "import galileo, dotenv; print('galileo', getattr(galileo,'__version__','unknown'), 'python-dotenv', getattr(dotenv,'__version__','unknown'))"
```

Note: `python-dotenv` does not always expose a `__version__` attribute; the important part is that the import succeeds.

7. Run the Crew

```zsh
# navigate to the root of the CrewAI project
cd research_crew
# while .venv is active
crewai run
```
