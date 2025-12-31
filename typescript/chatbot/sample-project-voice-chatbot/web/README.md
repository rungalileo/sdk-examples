# ElevenLabs + Galileo Voice Agent

> Runtime protection either requires Luna-2 running on the enterprise tier of Galileo, or [custom code-based metrics](https://v2docs.galileo.ai/concepts/metrics/custom-metrics/custom-metrics-ui-code). Sample codebase here assumes you are on enterprise tier. However, you can use runtime protection without the enterprise tier if you write your own code-based metrics instead of using Luna-2's built-in metrics (like toxicity or PII detection).

The voice agent will work without guardrails and Galileo logging and observability still works without Protect.

## 🎯 What This Example Shows

A Next.js application integrating ElevenLabs voice agents with Galileo AI observability and guardrails. There is a Python FastAPI backend service for this frontend that is located in this same repo under `python/chatbot/sample-project-voice-chatbot`, follow its `README.md` to complete the setup for the service layer. 


```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Next.js App   │────▶│  Python FastAPI      │────▶│  Galileo API    │
│   (Frontend)    │     │  (Galileo Logging)   │     │                 │
│   Port 3000     │     │  Port 8000           │     │                 │
└─────────────────┘     └──────────────────────┘     └─────────────────┘
        │
        ▼
┌─────────────────┐
│  ElevenLabs API │
│  (Voice Agent)  │
└─────────────────┘
```

The Python service handles all Galileo logging because the TypeScript SDK doesn't support `add_protect_span()`, which is required for Protect Status to display correctly in the Galileo console.

- **Real-time Voice Conversation**: WebRTC-based voice interaction with ElevenLabs AI agents
- **Galileo Observability**: Full conversation logging with sessions, traces, and LLM spans
- **Galileo Protect Guardrails**: Input/output filtering for safety and compliance

## 🚀 Quick Start

1. Install Dependencies

```bash
# Web app
cd web
npm install
```

2. Configure Environment

Copy `.env.example` to `.env.local` and fill in your credentials:

```bash
cp .env.example .env.local
```

Required environment variables: Note for ElevenLabs `ELEVENLABS_API_KEY` and `ELEVENLABS_AGENT_ID` sign up for a free tier, then create a voice agent under their `Agents Platform` to get the keys.

- `ELEVENLABS_API_KEY` - 
- `ELEVENLABS_AGENT_ID` - Your ElevenLabs agent ID
- `GALILEO_PYTHON_SERVICE_URL` - Python service URL (default: http://localhost:8000)

Note: Galileo API credentials are configured in the Python service's `.env` file.

3. Run the exanple:

```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to use the voice agent.

# 📚 Learn More
- [Galielo Protect Overview](https://v2docs.galileo.ai/concepts/protect/overview)
- [Galileo Runtime Rrotection](https://v2docs.galileo.ai/sdk-api/protect/invoke-protect)
- [Defining Rules for Runtime Protection](https://v2docs.galileo.ai/sdk-api/protect/rules)