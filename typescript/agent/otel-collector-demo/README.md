# OTEL TypeScript Collector Demo for Galileo

A self-contained TypeScript example showing how to send GenAI telemetry to Galileo through an OpenTelemetry Collector, with a local Jaeger UI for visual span inspection.

## Architecture

```
+------------------+       +-------------------+       +--------------------+
|  TypeScript App  | OTLP  |   OTEL Collector  | OTLP  |      Galileo       |
|  (Node.js, host) |------>|   (Docker)        |------>|  otel/v1/traces    |
|                  | HTTP  |                   | HTTP  |                    |
+------------------+ :4318 +------|------------+       +--------------------+
                                  |
                                  | OTLP/gRPC
                                  v
                         +-------------------+
                         |    Jaeger UI      |
                         |   (Docker)        |
                         |  localhost:16686  |
                         +-------------------+
```

**Data flow:**

1. The TypeScript app creates OTEL spans with GenAI semantic attributes
2. Spans are exported via OTLP/HTTP to the local OTEL Collector (port 4318)
3. The collector fans out to two destinations:
   - **Galileo** via OTLP/HTTP with Galileo auth headers
   - **Jaeger** via OTLP/gRPC for local visualization

The app sends **no Galileo-specific headers** — the collector owns the export config, which mirrors production deployments where the collector is a centralized gateway.

## Span Hierarchy

Each conversation turn is its own OTEL trace. Galileo groups them into a
single session because they share the same `session.id` attribute.

```
Session (Galileo groups traces by session.id)
│
├── Trace 1 ── invoke_agent "restaurant_assistant"
│              ├── chat             (LLM: decides to use web_search)
│              ├── execute_tool     (web_search: returns restaurant list)
│              └── chat             (LLM: synthesizes recommendation)
│
└── Trace 2 ── invoke_agent "restaurant_assistant"
               ├── chat             (LLM: decides to check availability)
               ├── execute_tool     (check_availability: returns time slots)
               └── chat             (LLM: presents reservation options)
```

## GenAI Attributes

| Span Type | Key Attributes |
|-----------|---------------|
| Agent root (`invoke_agent`) | `session.id`, `gen_ai.operation.name`, `gen_ai.agent.name` |
| LLM (`chat`) | `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.provider.name`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons` |
| Tool (`execute_tool`) | `gen_ai.operation.name`, `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result` |

Agent and LLM spans carry input/output via OTEL events: `gen_ai.user.message` and `gen_ai.choice`.

## Prerequisites

- Node.js 18+
- Docker and Docker Compose
- A Galileo account with API key

## Quick Start

```bash
# 1. Configure
cp .env.example .env
# Edit .env with your Galileo credentials

# 2. Install dependencies
npm install

# 3. Start infrastructure (Collector + Jaeger)
npm run infra:up

# 4. Run the demo
npm start              # Simulated mode (no OpenAI key needed)
# OR
npm run start:real     # Real OpenAI mode (requires OPENAI_API_KEY in .env)

# 5. Tear down
npm run infra:down
```

## npm Scripts Reference

| Script | Command | What it does |
|--------|---------|-------------|
| `npm start` | `npx tsx src/index.ts` | Runs the demo in simulated mode (mock LLM responses, no API keys needed) |
| `npm run start:real` | `USE_REAL_LLM=true npx tsx src/index.ts` | Runs the demo with real OpenAI API calls (requires `OPENAI_API_KEY`) |
| `npm run infra:up` | `docker compose up -d` | Starts the OTEL Collector and Jaeger containers in the background |
| `npm run infra:down` | `docker compose down` | Stops and removes the containers |
| `npm run build` | `tsc` | Compiles TypeScript to `dist/` (not required to run — `tsx` handles it) |

## Docker Services

`npm run infra:up` starts two containers defined in `docker-compose.yml`:

### 1. OTEL Collector (`otel-collector`)

- **Image:** `otel/opentelemetry-collector-contrib:0.115.0`
- **Role:** Receives OTLP traces from the TypeScript app and forwards them to Galileo and Jaeger. This is the central routing layer — the app itself has no knowledge of Galileo credentials.
- **Config:** Reads `otel-collector-config.yaml` (mounted as a volume). The config defines one receiver (OTLP on ports 4317/4318), a batch processor, and three exporters (Galileo, Jaeger, debug console).
- **Exposed ports:**

  | Port | Protocol | Purpose |
  |------|----------|---------|
  | `4317` | gRPC | OTLP gRPC receiver (available but not used by this demo) |
  | `4318` | HTTP | OTLP HTTP receiver — **the app sends traces here** |
  | `8888` | HTTP | Collector's own metrics (Prometheus format) |

- **Environment variables:** `GALILEO_CONSOLE_URL`, `GALILEO_API_KEY`, `GALILEO_PROJECT`, `GALILEO_LOG_STREAM` — all read from your `.env` file via docker-compose. The collector config references these with `${VAR}` syntax to set the Galileo export endpoint and auth headers.
- **Logs:** `docker compose logs -f otel-collector` — the `debug` exporter prints a summary line for every span batch, useful for confirming traces are flowing.

### 2. Jaeger (`jaeger`)

- **Image:** `jaegertracing/all-in-one:1.62`
- **Role:** Receives traces from the collector and provides a web UI for inspecting span trees, attributes, and timing. Runs an all-in-one deployment (collector + query + UI in a single container) with in-memory storage.
- **Exposed ports:**

  | Port | Protocol | Purpose |
  |------|----------|---------|
  | `16686` | HTTP | **Jaeger UI** — open http://localhost:16686 in your browser |
  | `4317` (internal) | gRPC | OTLP gRPC receiver — only the collector connects here (not mapped to host) |

- **No configuration needed:** Jaeger's OTLP collector is enabled via the `COLLECTOR_OTLP_ENABLED=true` environment variable. Storage is in-memory — traces are lost when the container stops, which is fine for a demo.

### Verifying the services are running

```bash
# Check container status
docker compose ps

# Expected output:
# NAME             IMAGE                                          STATUS
# jaeger           jaegertracing/all-in-one:1.62                  Up
# otel-collector   otel/opentelemetry-collector-contrib:0.115.0   Up

# Confirm the collector is healthy and listening
curl -s http://localhost:8888/metrics | head -5

# Confirm Jaeger UI is accessible
curl -s -o /dev/null -w "%{http_code}" http://localhost:16686
# Should print: 200
```

## What to Observe

### In Jaeger (http://localhost:16686)

1. Open http://localhost:16686 in your browser
2. In the **Service** dropdown, select **otel-ts-collector-demo**
3. Click **Find Traces** — you should see two traces (one per conversation turn)
4. Click on a trace to expand the span tree:
   - `invoke_agent` — root span (carries `session.id` and agent name)
     - `chat` — LLM call (decides which tool to use)
     - `execute_tool` — tool call (web_search or check_availability)
     - `chat` — LLM call (synthesizes final answer)
5. Click any span to inspect its **Tags** (attributes) and **Logs** (events):
   - Agent spans show `gen_ai.agent.name` and input/output events
   - LLM spans show `gen_ai.request.model`, token counts, and `gen_ai.choice` events
   - Tool spans show `gen_ai.tool.name`, arguments, and result

### In Galileo

1. Navigate to your project (the `GALILEO_PROJECT` value from `.env`)
2. Select the log stream (`GALILEO_LOG_STREAM` from `.env`)
3. View traces with session grouping — both turns grouped under one session
4. Inspect LLM inputs/outputs, token usage, and tool calls
5. Check the span hierarchy matches the tree above

## How Galileo Headers Flow

The OTEL Collector is configured with Galileo credentials in `otel-collector-config.yaml`:

```yaml
exporters:
  otlphttp/galileo:
    traces_endpoint: "${GALILEO_CONSOLE_URL}/api/galileo/otel/v1/traces"
    headers:
      Galileo-API-Key: "${GALILEO_API_KEY}"
      project: "${GALILEO_PROJECT}"
      logstream: "${GALILEO_LOG_STREAM}"
```

These env vars flow from your `.env` → `docker-compose.yml` (environment section) → collector container → `otel-collector-config.yaml` (variable substitution). The app never touches them.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No spans in Jaeger | Check collector logs: `docker compose logs otel-collector` |
| No spans in Galileo | Verify API key and console URL in `.env`, then check collector logs for HTTP errors |
| Collector won't start | Check config syntax: `docker compose logs otel-collector` will show parse errors |
| Port 4318 in use | Stop other OTEL collectors or change the port mapping in `docker-compose.yml` |
| Jaeger UI not loading | Verify the container is running: `docker compose ps` |
| `ECONNREFUSED :4318` | Infrastructure isn't running — run `npm run infra:up` first |

For verbose OTEL SDK logging, change `DiagLogLevel.INFO` to `DiagLogLevel.DEBUG` in `src/tracing.ts`.

## Learn More

- [Galileo Documentation](https://v2docs.galileo.ai/what-is-galileo)
- [OpenTelemetry Collector ](https://opentelemetry.io/docs/collector/)