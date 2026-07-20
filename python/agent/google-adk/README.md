# Google ADK + Splunk AO Example Project

This is an example project demonstrating how to use Splunk Agent Observability (Splunk AO) with the Google ADK. This uses the simple [quickstart from the Google ADK documentation](https://google.github.io/adk-docs/get-started/python/#create-an-agent-project), and adds Splunk AO tracing.

## Getting Started

To get started with this project, you'll need to have Python 3.10 or later installed. You can then install the required dependencies in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --index-url https://pypi.org/simple -r requirements.txt
```

## Configure environment variables

You will need to configure environment variables to use this project. Copy the `.env.example` file to `.env`, then update the environment variables in the `.env` file with your values:

```ini
# ── Splunk AO ─────────────────────────────────────────────────────────────────
SPLUNK_AO_API_KEY=<your-api-key>
SPLUNK_AO_PROJECT=google-adk
SPLUNK_AO_LOG_STREAM=<your-log-stream>

# Required for self-hosted deployments:
SPLUNK_AO_API_URL=https://<splunk-ao-api-host>

# ── LLM Provider ──────────────────────────────────────────────────────────────
# Option A: OpenAI-compatible (Azure OpenAI or standard OpenAI)
OPENAI_API_KEY=<your-key>
OPENAI_BASE_URL=https://<resource>.cognitiveservices.azure.com/openai/v1/  # Azure only

# Option B: Google Gemini
# GOOGLE_GENAI_USE_VERTEXAI=0
# GOOGLE_API_KEY=<your-google-key>
```

> **Self-hosted API URL** — `SPLUNK_AO_API_URL` sets the Splunk AO API host directly.
> This is required for self-hosted deployments where the hostname does not contain
> `"console"` (e.g. `agent-observability.rc0.signalfx.com`).

## Usage

Once the dependencies are installed and the `.env` file is configured, run the example using the `adk` command:

```bash
adk run my_agent
```

Traces will be captured and logged to Splunk AO.

## Project Structure

```
google-adk/
├── my_agent/          # The main agent application
│   ├── __init__.py
│   ├── agent.py
│   └── .env.example   # Environment variable template
├── requirements.txt   # Python project requirements
└── README.md          # Project documentation
```
