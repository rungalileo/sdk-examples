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
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# ElevenLabs SDK for voice conversations
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# Galileo SDK for logging and tracing
from galileo import GalileoLogger, Message, MessageRole


# =============================================================================
# GALILEO LOGGING SETUP
# =============================================================================
#
# GalileoLogger provides observability for AI applications by capturing:
# - Sessions: Group related conversations (e.g., a user's chat session)
# - Traces: Individual request-response cycles within a session
# - Spans: Detailed steps within a trace (e.g., LLM calls, tool use)
#
# This allows you to monitor conversation quality, debug issues, and
# analyze patterns in your AI application.
# =============================================================================


class GalileoHandler:
    """Handles Galileo logging for voice conversations.

    Captures each conversation turn (user speech -> agent response) as a trace,
    with the LLM interaction logged as a span within that trace.
    """

    def __init__(self):
        self._logger: Optional[GalileoLogger] = None
        self._session_id: Optional[str] = None
        self._turn_count = 0

        # Load Galileo config from environment
        self._project_name = os.getenv("GALILEO_PROJECT_NAME", "elevenlabs-voice-poc")
        self._log_stream = os.getenv("GALILEO_LOG_STREAM", "voice-chatbot")

        self._init_logger()

    def _init_logger(self):
        """Initialize the Galileo Logger.

        The logger connects to a specific project and log stream in Galileo.
        Log streams help organize logs by environment (dev, staging, prod)
        or by feature area.
        """
        try:
            self._logger = GalileoLogger(
                project=self._project_name,
                log_stream=self._log_stream,
            )
            print(f"[GALILEO] Logger initialized for project: {self._project_name}")
        except Exception as e:
            print(f"[GALILEO] Logger init failed: {e}")

    def start_conversation(self, session_id: str):
        """Start a new conversation session in Galileo.

        A session groups all the turns of a single conversation together,
        making it easy to view the full conversation history in the Galileo UI.
        """
        self._session_id = session_id
        self._turn_count = 0

        if self._logger:
            # external_id links this session to your own session tracking
            self._logger.start_session(name=f"Voice-{session_id[:8]}", external_id=session_id)
            print(f"[GALILEO] Started session: {session_id[:8]}")

    def log_user_turn(self, transcript: str) -> None:
        """Log when the user speaks.

        This starts a new trace for this conversation turn.
        The trace captures the full request-response cycle.
        """
        self._turn_count += 1
        self._last_user_input = transcript

        if self._logger:
            try:
                # Each turn gets its own trace for clear organization
                self._logger.start_trace(input=transcript, name=f"Turn-{self._turn_count}")
            except Exception as e:
                print(f"[GALILEO] Trace start error: {e}")

    def log_agent_turn(self, response: str) -> None:
        """Log when the agent responds.

        This adds an LLM span to capture the model interaction,
        then concludes the trace with the final output.
        """
        if self._logger:
            try:
                user_input = getattr(self, "_last_user_input", "")

                # Log the LLM interaction as a span
                # Even though ElevenLabs handles the actual LLM call,
                # we log it here for visibility into the conversation flow
                self._logger.add_llm_span(
                    input=user_input,
                    output=Message(content=response, role=MessageRole.assistant),
                    model="elevenlabs-agent",
                )

                # Conclude the trace with the final response
                self._logger.conclude(output=response)

                # Flush to send logs to Galileo immediately
                self._logger.flush()
            except Exception as e:
                print(f"[GALILEO] Logging error: {e}")

    def end_conversation(self):
        """End the conversation session and cleanup.

        Ensures all logs are flushed and the session is properly closed.
        """
        if self._logger:
            try:
                self._logger.flush()
                self._logger.clear_session()
                print(f"[GALILEO] Session ended ({self._turn_count} turns)")
            except Exception as e:
                print(f"[GALILEO] Cleanup error: {e}")

        self._session_id = None
        self._turn_count = 0


# Singleton instance for the Galileo handler
_galileo_handler: Optional[GalileoHandler] = None


def get_galileo_handler() -> GalileoHandler:
    """Get or create the Galileo handler singleton."""
    global _galileo_handler
    if _galileo_handler is None:
        _galileo_handler = GalileoHandler()
    return _galileo_handler


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
