# ElevenLabs Voice Chatbot with Galileo Protect

A terminal-based voice chatbot that lets you have real-time voice conversations with an ElevenLabs AI agent, with Galileo Protect guardrails for content moderation.

## What This Example Shows

- Interactive voice chat in your terminal (speak via microphone, hear responses via speakers)
- Real-time guardrails using Galileo Protect to moderate user input and agent output
- Conversation logging and tracing with Galileo Observe
- Session metrics tracking (latency, turn counts, character counts)

## Quick Start

1. Install system dependencies:
   ```bash
   brew install portaudio  # Required for audio support on macOS
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. Run the voice chat:
   ```bash
   python conversation.py
   ```

   For best results use a headset with micrphone. The app will start listening through your microphone. Speak to chat with the AI agent and hear responses through your speakers. Press `Ctrl+C` to end the session.

## Configuration

Edit `.env` with your credentials. Note for `ELEVENLABS_*` variables you can signup with a free tier of elevenlabs and use their Agents Platform to create a voice agent to obtain the required API key and Agent Id:

| Variable | Description |
|----------|-------------|
| `ELEVENLABS_API_KEY` | Your ElevenLabs API key |
| `ELEVENLABS_AGENT_ID` | Your ElevenLabs Agent ID |
| `GALILEO_API_KEY` | Your Galileo API key |
| `GALILEO_CONSOLE_URL` | Galileo console URL (optional) |
| `GALILEO_PROJECT_NAME` | Project name for logging |
| `GALILEO_PROTECT_STAGE_ID` | Protect stage ID for guardrails (see below) |

### Creating a Galileo Protect Stage

To enable guardrails, you need to create a Galileo Protect stage. Run the included script:

```bash
python scripts/create_stage.py
```

This will create a protect stage with an input toxicity rule and output the stage ID. Copy this ID to your `.env` file as `GALILEO_PROTECT_STAGE_ID`.

## Requirements

- Python 3.9+
- Microphone and headphones (to avoid audio feedback)

## Learn More

- [Galileo Documentation](https://docs.galileo.ai/)
- [Runtime Protection](https://v2docs.galileo.ai/concepts/protect/overview)
- [ElevenLabs Conversational AI](https://elevenlabs.io/docs/conversational-ai)
