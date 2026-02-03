"""ElevenLabs Voice Chatbot with Galileo Logging

A tutorial example showing how to:
1. Set up a real-time voice conversation with ElevenLabs Conversational AI
2. Log conversation turns to Galileo for observability and tracing

Prerequisites:
- macOS with portaudio installed (brew install portaudio)
- ElevenLabs API key and Agent ID
- Galileo API key and project configured
"""

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# ElevenLabs SDK for voice conversations
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# Galileo handler for logging and tracing
from galileo_handler import get_galileo_handler

# =============================================================================
# ELEVENLABS CONVERSATION CALLBACKS
# =============================================================================
#
# ElevenLabs Conversational AI uses callbacks to notify your app when
# events occur during the conversation:
# - User speaks and their speech is transcribed
# - Agent generates and speaks a response
#
# We use these callbacks to log each turn to Galileo.
# =============================================================================


def on_agent_response(response: str) -> None:
    """Called when the ElevenLabs agent responds.

    This callback fires after the agent generates a response.
    We log this to Galileo to complete the conversation turn trace.
    """
    print(f"\n[AGENT] {response}")

    galileo = get_galileo_handler()
    galileo.log_agent_turn(response)


def on_user_transcript(transcript: str) -> None:
    """Called when user speech is transcribed.

    This callback fires after your speech is converted to text.
    We log this to Galileo to start a new conversation turn trace.
    """
    print(f"\n[USER] {transcript}")

    galileo = get_galileo_handler()
    galileo.log_user_turn(transcript)


# =============================================================================
# MAIN CONVERSATION LOOP
# =============================================================================


def run_voice_conversation():
    """Run a voice conversation with ElevenLabs + Galileo logging.

    This function:
    1. Initializes the ElevenLabs client and Galileo logger
    2. Creates a conversation with audio input/output
    3. Runs until the user presses Ctrl+C
    4. Logs all turns to Galileo for observability
    """
    # Load ElevenLabs credentials from environment
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    elevenlabs_agent_id = os.getenv("ELEVENLABS_AGENT_ID")

    if not elevenlabs_api_key or not elevenlabs_agent_id:
        print("Error: ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID must be set in .env")
        return

    # Initialize ElevenLabs client with your API key
    client = ElevenLabs(api_key=elevenlabs_api_key)

    # Initialize Galileo and start a new session
    galileo = get_galileo_handler()
    session_id = str(uuid.uuid4())
    galileo.start_conversation(session_id)

    print("\n" + "=" * 60)
    print("ElevenLabs Voice Chatbot + Galileo Logging")
    print(f"Session ID: {session_id}")
    print("*** USE HEADPHONES to avoid audio feedback loop ***")
    print("Speak into your microphone to talk to the agent")
    print("Press Ctrl+C to end the session")
    print("=" * 60 + "\n")

    # Create the ElevenLabs conversation
    # - DefaultAudioInterface() handles microphone input and speaker output
    # - Callbacks connect events to our Galileo logging functions
    conversation = Conversation(
        client=client,
        agent_id=elevenlabs_agent_id,
        requires_auth=True,
        audio_interface=DefaultAudioInterface(),
        callback_agent_response=on_agent_response,
        callback_user_transcript=on_user_transcript,
    )

    # Start the conversation (this begins listening)
    print("[INFO] Starting conversation... Speak now!")
    conversation.start_session()

    # wait for the conversation to end (blocks until Ctrl+C or session ends)
    try:
        conversation.wait_for_session_end()
    except KeyboardInterrupt:
        print("\n[INFO] Ending conversation...")
        conversation.end_session()

    # End the Galileo session and flush remaining logs
    galileo.end_conversation()
    print("[INFO] Conversation ended - logs sent to Galileo")


if __name__ == "__main__":
    run_voice_conversation()
