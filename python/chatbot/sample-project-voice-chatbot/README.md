# Galileo Protect Python Service

> Runtime protection either requires Luna-2 running on the enterprise tier of Galileo, or [custom code-based metrics](https://v2docs.galileo.ai/concepts/metrics/custom-metrics/custom-metrics-ui-code). Sample codebase here assumes you are on enterprise tier. However, you can use runtime protection without the enterprise tier if you write your own code-based metrics instead of using Luna-2's built-in metrics (like toxicity or PII detection).

The voice agent will work without guardrails and Galileo logging and observability still works without Protect.

FastAPI microservice that bridges the Next.js app with Galileo's Python SDK for proper Protect Status logging.
The Next.js app for this backend is located in this same repo under `typescript/chatbot/sample-project-voice-chatbot/web`. Please follow the Nextjs app's `README.md` to complete the setup.

The Galileo TypeScript SDK doesn't support `add_protect_span()`, which means Protect Status shows "N/A" in the Galileo console when using TypeScript alone. This Python service uses the full Galileo Python SDK to properly log Protect spans.

## What This Example Shows

1. Next.js calls `/log-conversation-turn` with conversation data
2. Service starts/continues a Galileo trace for the session
3. Invokes `invoke_protect()` for input guardrails
4. Adds protect span via `add_protect_span()` in the same trace
5. Logs the LLM response span
6. Invokes output guardrails if input wasn't blocked
7. Concludes and flushes the trace
8. Protect Status now shows correctly in Galileo console

## Quick Start

```bash
# Create virtual environment
cd service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Set up environment variables:

```bash
cp .env.example .env
```

Required variables:
- `GALILEO_API_KEY` - Your Galileo API key
- `GALILEO_CONSOLE_URL` - Galileo console URL (e.g., `https://app.galileo.ai`)
- `GALILEO_PROJECT_NAME` - Your Galileo project name
Optional:
- `GALILEO_LOG_STREAM` - Log stream name (default: `voice-conversations`)
- `GALILEO_PROTECT_ENABLED` - Set to `true` to enable guardrails
- `GALILEO_PROTECT_STAGE_ID` - Protect stage ID (required for guardrails) - see below on how to get one
- `PORT` - Service port (default: `8000`)

To enable guardrails, set `GALILEO_PROTECT_ENABLED=true` and provide a Protect stage ID. Use the script in the `scripts/` directory:

```bash
cd scripts
pip install -r requirements.txt
python create_protect_stage.py
```

The script will:
1. Create a Protect stage with toxicity and PII detection rules
2. If the stage already exists, updates it with the current rulesets
3. Print the `GALILEO_PROTECT_STAGE_ID` to add to your `.env`

See [scripts/create_protect_stage.py](scripts/create_protect_stage.py) for configuration options.


3. Run the example:
```bash
cd service
python main.py
```

Service starts on ` http://0.0.0.0:8000` and also you must have followed the setup and deployment of this service's frontend Nextjs web app under `typescript/chatbot/sample-project-voice-chatbot/web`

# Learn More
- [Galielo Protect Overview](https://v2docs.galileo.ai/concepts/protect/overview)
- [Galileo Runtime Rrotection](https://v2docs.galileo.ai/sdk-api/protect/invoke-protect)
- [Defining Rules for Runtime Protection](https://v2docs.galileo.ai/sdk-api/protect/rules)
