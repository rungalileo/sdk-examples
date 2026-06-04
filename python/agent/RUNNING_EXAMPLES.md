# Running the Splunk AO Python SDK Examples

This document covers the two agent examples verified working against a self-hosted Splunk AO
(formerly Galileo) deployment. Copy `.env.example` to `.env`, fill in the values, and run.

---

## Prerequisites

| Requirement | Detail |
|---|---|
| Python | 3.10 or newer (examples were run with **3.13**) |
| Network | Access to your Splunk AO instance |
| Splunk AO UI | Your `SPLUNK_AO_CONSOLE_URL` |

---

## Example 1 — LangChain Agent (Splunk AO SDK)

**Path:** `python/agent/langchain-agent/`

Uses the `galileo` Python SDK directly (`galileo_context` + `GalileoCallback`).
Traces are sent via the Splunk AO REST API.

### .env file

Copy `.env.example` to `.env` and fill in your values:

```ini
# ── Splunk AO ─────────────────────────────────────────────────────────────────
SPLUNK_AO_API_KEY=<your-api-key>
SPLUNK_AO_PROJECT=<your-project-name>
SPLUNK_AO_LOG_STREAM=<your-log-stream-name>

# Self-hosted deployments only:
# SPLUNK_AO_CONSOLE_URL=https://<your-splunk-ao-host>

# ── LLM Provider ──────────────────────────────────────────────────────────────
# Option A – standard OpenAI
# OPENAI_API_KEY=<your-key>
# OPENAI_MODEL=gpt-4o-mini

# Option B – Azure OpenAI
# OPENAI_API_KEY=<azure-key>
# OPENAI_BASE_URL=https://<resource>.cognitiveservices.azure.com/openai/v1/
# OPENAI_MODEL=gpt-4o-mini
```

### Setup and run

```bash
cd python/agent/langchain-agent

# Create venv (Python 3.10+ required)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --index-url https://pypi.org/simple -r requirements.txt

# Run
python main.py
```

### Expected output

```
Agent Response:
Hello, Erin! 👋
```

Exit code 0 with no errors means traces were flushed successfully.

---

## Example 2 — Strands Agent (OpenTelemetry / OTLP)

**Path:** `python/agent/strands-agents/`

Uses the `strands-agents` SDK with OpenTelemetry. Spans are exported in OTLP format
directly to the Splunk AO OTel endpoint — no Galileo SDK is imported.

### .env file

Copy `.env.example` to `.env` and fill in your values:

```ini
# ── LLM Provider ──────────────────────────────────────────────────────────────
# Option A: AWS Bedrock (default Strands provider)
# AWS_BEARER_TOKEN_BEDROCK=<token>

# Option B: Azure OpenAI
# OPENAI_API_KEY=<azure-key>
# OPENAI_BASE_URL=https://<resource>.cognitiveservices.azure.com/openai/v1/
# OPENAI_MODEL=gpt-4o-mini

# ── Splunk AO ─────────────────────────────────────────────────────────────────
SPLUNK_AO_API_KEY=<your-api-key>
SPLUNK_AO_PROJECT=<your-project-name>
SPLUNK_AO_LOG_STREAM=<your-log-stream-name>

# Self-hosted OTel endpoint (leave unset for Splunk AO Cloud):
# SPLUNK_AO_API_ENDPOINT=https://<splunk-ao-api-host>/otel/traces
```

### Setup and run

```bash
cd python/agent/strands-agents

# Create venv (Python 3.10+ required)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --index-url https://pypi.org/simple -r requirements.txt

# Run
python agent.py
```

### Expected output

```
Tool #1: current_time
Tool #2: calculator
Tool #3: letter_counter
Here are the results for your requests:
1. The current time is <ISO timestamp>.
2. The result of 3111696 / 74088 is 42.
3. The number of letter R's in "strawberry" is 3.
```

Exit code 0 with no Python exceptions means the OTel spans were exported.

---

## Key notes

1. **pip index** — If the system pip is configured with a private registry, pass
   `--index-url https://pypi.org/simple` when installing to avoid 401 errors.

2. **Python version** — `strands-agents` uses `dataclasses(kw_only=True)` which requires
   Python 3.10+. The system default may be older; use a version manager (pyenv, etc.).

3. **Self-hosted API URL** — The `galileo` SDK derives the API URL from `SPLUNK_AO_CONSOLE_URL`.
   If auto-derivation produces the wrong URL for your deployment, set `GALILEO_API_URL` explicitly
   (this will be renamed to `SPLUNK_AO_API_URL` in a follow-up ticket).

4. **OTel endpoint variable** — `agent.py` reads `SPLUNK_AO_API_ENDPOINT` and assigns it to
   `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` at runtime. The `.env` file is the only place you need
   to change the endpoint.
