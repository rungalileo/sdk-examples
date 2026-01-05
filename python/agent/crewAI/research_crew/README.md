# CrewAI and Galileo Cookbook

This tutorial is a completed version of the [CrewAI quickstart](https://docs.crewai.com/en/quickstart) and adds the
Galileo [CrewAIEventListener](https://v2docs.galileo.ai/sdk-api/python/reference/handlers/crewai/handler),
an event handler implemented on top of OpenTelemetry (OTel). For more information, see
Galileo’s [Add Galileo to a CrewAI Application](https://v2docs.galileo.ai/how-to-guides/third-party-integrations/add-galileo-to-crewai/add-galileo-to-crewai)
how-to guide.

Below you'll find concise setup steps, configuration notes, and a short primer on Galileo so you know why we add it and what it provides.

## Resources

The relevant guides:

- [Add Galileo to CrewAI](https://v2docs.galileo.ai/how-to-guides/third-party-integrations/add-galileo-to-crewai/add-galileo-to-crewai)
- [CrewAI quickstart](https://docs.crewai.com/en/guides/crews/first-crew)

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
- `uv` installed and available.
- [CrewAI CLI](https://docs.crewai.com/en/installation) installed and available.
- A [Galileo API key](https://app.galileo.ai/)
- A [Serper API Key](https://serper.dev/)
- An [OpenAI Key](https://platform.openai.com/)

## Quick setup

Run these steps from the repository root.

1. Clone and open the repo

```zsh
git clone https://github.com/rungalileo/sdk-examples.git
cd sdk-examples/python/agent/crewAI/research_crew
```

2. Copy the .env.example and configure credentials

```zsh
cp .env.example .env
```

In addition to API keys, you’ll need to specify a Galileo project and log stream (e.g. GALILEO_PROJECT and GALILEO_LOG_STREAM). All CrewAI run data will be logged to this destination in Galileo. See
[Understanding the Galileo Integration](#understanding-the-galileo-integration) for more detail.

3. Install project dependencies into the active environment:

```zsh
crewai install
```

4. Run the Crew

```zsh
crewai run
```

## Understanding the Galileo Integration

Galileo integrates with CrewAI by registering an event listener that captures Crew execution events (e.g., agent actions, tool calls, model responses) and forwards them to Galileo for observability and evaluation. Under the hood, this integration is built on OpenTelemetry (OTel) for standardized tracing and telemetry collection.

### Register the event listener

At the beginning of your run() function (or before starting the Crew), instantiate the Galileo event listener:

```python

def run():
    # Create the event listener (registers itself with CrewAI)
    CrewAIEventListener()

    # The rest of your existing code goes here
```

This is insturmented in [main.py](research_crew/src/research_crew/main.py).

### What this does

Creating a CrewAIEventListener() instance is all that’s required to enable Galileo for a CrewAI run. When instantiated, the listener:

- Automatically registers itself with CrewAI
- Uses OpenTelemetry (OTel) to instrument Crew execution events
- Reads Galileo configuration from environment variables
- Logs all run data to the Galileo project and log stream specified by
  `GALILEO_PROJECT` and `GALILEO_LOG_STREAM`

No additional configuration or code changes are required. All data from this run is logged to the Galileo project and log stream specified by your environment configuration (for example, GALILEO_PROJECT and GALILEO_LOG_STREAM).

## CrewAI Support

For support, questions, or feedback regarding the ResearchCrew Crew or crewAI.

- Visit the [CrewAI documentation](https://docs.crewai.com)
- Reach out to CrewAI through their [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join the CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with the CrewAI docs](https://chatg.pt/DWjSBZn)
