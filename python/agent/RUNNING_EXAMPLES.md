# Running the Splunk AO Python SDK Examples

This document covers the two agent examples verified working against self-hosted Splunk AO
(formerly Galileo) deployments. Copy `.env.example` to `.env`, fill in the values, and run.

---

## Prerequisites

| Requirement | Detail |
|---|---|
| Python | 3.10 or newer |
| Network | Access to your Splunk AO instance |

---

## Example 1 — LangChain Agent (Splunk AO SDK)

**Path:** `python/agent/langchain-agent/`

Uses the Splunk AO Python SDK directly (`galileo_context` + `SplunkAOCallback`).
Traces are sent via the Splunk AO REST API.

### .env file

Copy `.env.example` to `.env` and fill in your values:

```ini
# ── Splunk AO ─────────────────────────────────────────────────────────────────
SPLUNK_AO_API_KEY=<your-api-key>
SPLUNK_AO_PROJECT=<your-project-name>
SPLUNK_AO_LOG_STREAM=<your-log-stream-name>

# Required for self-hosted deployments:
SPLUNK_AO_API_URL=https://<splunk-ao-api-host>

# ── LLM Provider ──────────────────────────────────────────────────────────────
# Option A – standard OpenAI
# OPENAI_API_KEY=<your-key>
# OPENAI_MODEL=gpt-4o-mini

# Option B – Azure OpenAI
# OPENAI_API_KEY=<azure-key>
# OPENAI_BASE_URL=https://<resource>.cognitiveservices.azure.com/openai/v1/
# OPENAI_MODEL=gpt-4o-mini
```

### Minimum required vars

| Var | Purpose |
|---|---|
| `SPLUNK_AO_API_KEY` | Authentication |
| `SPLUNK_AO_PROJECT` | Project to log traces into |
| `SPLUNK_AO_LOG_STREAM` | Log stream to log traces into |
| `SPLUNK_AO_API_URL` | API host for self-hosted deployments (see note below) |

> **Self-hosted API URL** — The SDK cannot auto-derive the API URL for most Splunk AO
> deployment hostnames. Set `SPLUNK_AO_API_URL` explicitly.
> `SPLUNK_AO_CONSOLE_URL` is only needed as a fallback when `SPLUNK_AO_API_URL` is absent.

### Setup and run

```bash
cd python/agent/langchain-agent

python3 -m venv .venv
source .venv/bin/activate

pip install --index-url https://pypi.org/simple -r requirements.txt

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
# ── Splunk AO ─────────────────────────────────────────────────────────────────
SPLUNK_AO_API_KEY=<your-api-key>
SPLUNK_AO_PROJECT=<your-project-name>
SPLUNK_AO_LOG_STREAM=<your-log-stream-name>

# Required for self-hosted deployments:
SPLUNK_AO_API_ENDPOINT=https://<splunk-ao-api-host>/otel/traces

# ── LLM Provider ──────────────────────────────────────────────────────────────
# Option B: Azure OpenAI
OPENAI_API_KEY=<azure-key>
OPENAI_BASE_URL=https://<resource>.cognitiveservices.azure.com/openai/v1/
OPENAI_MODEL=gpt-4o-mini
```

### Minimum required vars

| Var | Purpose |
|---|---|
| `SPLUNK_AO_API_KEY` | Sent as `Galileo-API-Key` OTLP header |
| `SPLUNK_AO_PROJECT` | Sent as `project` OTLP header |
| `SPLUNK_AO_LOG_STREAM` | Sent as `logstream` OTLP header |
| `SPLUNK_AO_API_ENDPOINT` | OTLP HTTP endpoint; defaults to `https://api.galileo.ai/otel/traces` |

> **Span flushing** — `agent.py` calls `strands_telemetry.tracer_provider.shutdown()`
> at exit. This is required: `BatchSpanProcessor` runs a daemon thread that is killed
> before flushing if `shutdown()` is not called explicitly.

### Setup and run

```bash
cd python/agent/strands-agents

python3 -m venv .venv
source .venv/bin/activate

pip install --index-url https://pypi.org/simple -r requirements.txt

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

## Notes

1. **pip index** — If the system pip is configured with a private registry, pass
   `--index-url https://pypi.org/simple` when installing to avoid 401 errors.

2. **Python version** — `strands-agents` uses `dataclasses(kw_only=True)` which requires
   Python 3.10+.

3. **LangChain vs Strands env vars** — These examples use different mechanisms:
   - LangChain uses the Splunk AO REST API → needs `SPLUNK_AO_API_URL`
   - Strands uses OTLP directly → needs `SPLUNK_AO_API_ENDPOINT`
   Neither needs `SPLUNK_AO_CONSOLE_URL` when the API URL/endpoint is set explicitly.
