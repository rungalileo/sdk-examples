# ElevenLabs Voice Chatbot with Galileo

> **Note:** This example has been tested on macOS only.

A terminal-based voice chatbot that lets you have real-time voice conversations with an ElevenLabs AI agent, with conversation logging and tracing via Galileo.

## What This Example Shows

- Interactive voice chat in your terminal (speak via microphone, hear responses via speakers)
- Conversation logging and tracing with Galileo
- Session tracking with turn counts
- Integration pattern for logging voice-based AI interactions

## Quick Start

1. Install system dependencies (macOS):
   ```bash
   brew install portaudio
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
   python main.py
   ```

   For best results use a headset with microphone. The app will start listening through your microphone. Speak to chat with the AI agent and hear responses through your speakers. Press `Ctrl+C` to end the session.

## Configuration

Edit `.env` with your credentials. Note for `ELEVENLABS_*` variables you can [signup with a free tier](https://elevenlabs.io/app/sign-up?platform=agents) of ElevenLabs and use their Agents Platform to create a voice agent to obtain the required API key and Agent Id:

| Variable | Description |
|----------|-------------|
| `ELEVENLABS_API_KEY` | Your ElevenLabs API key |
| `ELEVENLABS_AGENT_ID` | Your ElevenLabs Agent ID |
| `GALILEO_API_KEY` | Your Galileo API key |
| `GALILEO_CONSOLE_URL` | Galileo console URL (optional) |
| `GALILEO_PROJECT_NAME` | Project name for logging |

## Requirements

- Python 3.10+
- Microphone and headphones (to avoid audio feedback)


## Learn More

- [Video tutorial](https://youtu.be/1QNEhDV2r5U)
- [Galileo Documentation](https://v2docs.galileo.ai/what-is-galileo)
- [ElevenLabs Conversational AI](https://elevenlabs.io/docs/conversational-ai)
