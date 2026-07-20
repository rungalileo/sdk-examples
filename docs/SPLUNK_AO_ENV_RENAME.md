# Splunk AO Environment Variable Rename Spec

**Jira:** HYBIM-713 · HYBIM-716 · HYBIM-727  
**Status:** Implemented

---

## Summary

All `GALILEO_*` environment variables used by the Python SDK examples have been renamed
to `SPLUNK_AO_*` as part of the Splunk Agent Observability rebrand.

The SDK (`splunk-ao-python`) bridges `SPLUNK_AO_*` → `GALILEO_*` internally so that
`galileo-core` (an upstream dependency not yet rebranded) continues to work transparently.

---

## Rename Map

| Old (`GALILEO_*`) | New (`SPLUNK_AO_*`) | Used by |
|---|---|---|
| `GALILEO_API_KEY` | `SPLUNK_AO_API_KEY` | both |
| `GALILEO_PROJECT` | `SPLUNK_AO_PROJECT` | both |
| `GALILEO_LOG_STREAM` | `SPLUNK_AO_LOG_STREAM` | both |
| `GALILEO_CONSOLE_URL` | `SPLUNK_AO_CONSOLE_URL` | langchain (optional) |
| `GALILEO_API_URL` | `SPLUNK_AO_API_URL` | langchain |
| `GALILEO_API_ENDPOINT` | `SPLUNK_AO_API_ENDPOINT` | strands (OTel) |

---

## SDK Bridge (`config.py`)

`SplunkAOConfig._bridge_env_vars()` propagates `SPLUNK_AO_*` values to their `GALILEO_*`
equivalents at initialisation time. Only bridges values not already set — explicit
`GALILEO_*` overrides win.

```python
_BRIDGE = [
    ("SPLUNK_AO_API_KEY",      "GALILEO_API_KEY"),
    ("SPLUNK_AO_API_URL",      "GALILEO_API_URL"),
    ("SPLUNK_AO_CONSOLE_URL",  "GALILEO_CONSOLE_URL"),
    ("SPLUNK_AO_PROJECT",      "GALILEO_PROJECT"),
    ("SPLUNK_AO_LOG_STREAM",   "GALILEO_LOG_STREAM"),
    ...
]
```

---

## Code Changes

### `langchain-agent/main.py`

- Import `SplunkAOCallback` from `splunk_ao.handlers.langchain` (handler code moved to
  `splunk_ao` namespace after rebrand; `galileo.handlers.langchain` is now empty).
- Read `SPLUNK_AO_PROJECT` / `SPLUNK_AO_LOG_STREAM` directly from env.
- Move `load_dotenv()` before all SDK imports so env vars are set before
  pydantic-settings initialises `GalileoConfig`.

### `strands-agents/agent.py`

- Renamed `GALILEO_API_KEY/PROJECT/LOG_STREAM/API_ENDPOINT` reads to `SPLUNK_AO_*`.
- Move `load_dotenv()` and all `os.environ` assignments before strands imports so OTel
  env vars are present before `StrandsTelemetry` initialises.
- Added explicit `strands_telemetry.tracer_provider.shutdown()` at exit.
  `BatchSpanProcessor` runs a daemon thread — without `shutdown()` pending spans are
  dropped when the process exits.

### `strands-agents/requirements.txt`

- `strands-agents` → `strands-agents[openai]` (Azure OpenAI model support).

---

## Self-hosted Deployment Notes

### LangChain (SDK / REST API)

`galileo-core` auto-derives the API URL from `GALILEO_CONSOLE_URL` using
`console_url.replace("console", "api")`. This breaks for hostnames that do not contain
the substring `"console"` (e.g. `agent-observability.rc0.signalfx.com`).

**Fix:** set `SPLUNK_AO_API_URL` explicitly. The bridge maps it to `GALILEO_API_URL`
which `galileo-core` uses directly, bypassing auto-derivation.

### Strands (OTLP)

The strands agent sends spans directly to the OTLP HTTP endpoint — no SDK auth flow
involved. Set `SPLUNK_AO_API_ENDPOINT` to the full `/otel/traces` path.
`SPLUNK_AO_API_URL` and `SPLUNK_AO_CONSOLE_URL` are irrelevant for strands.
