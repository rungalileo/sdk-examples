"""ElevenLabs Conversation using official SDK - supports voice input/output."""

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

from config import get_settings
from galileo_handler import get_galileo_handler


# Initialize Galileo handler
_galileo = None
_conversation = None


def _get_galileo():
    """Lazy initialization of Galileo handler."""
    global _galileo
    if _galileo is None:
        _galileo = get_galileo_handler()
    return _galileo


def on_agent_response(response: str) -> None:
    """Called when agent responds - logs to Galileo."""
    print(f"\n[AGENT] {response}")

    galileo = _get_galileo()
    result = galileo.log_agent_turn(response)
    if result.get("blocked"):
        print(f"[FAKE_GUARDRAIL] Agent response flagged: {result.get('reason')}")


def on_user_transcript(transcript: str) -> None:
    """Called when user speech is transcribed - logs to Galileo."""
    global _conversation
    print(f"\n[USER] {transcript}")

    galileo = _get_galileo()
    result = galileo.log_user_turn(transcript)
    if result.get("blocked"):
        print(f"\n[GALILEO PROTECT] *** INPUT BLOCKED *** {result.get('reason')}")

        # Get the override message from Galileo Protect
        override_message = result.get("override_message")

        if override_message:
            # End current conversation session first
            if _conversation:
                print(f"[GALILEO PROTECT] Ending conversation session...")
                _conversation.end_session()

            # Pause briefly to let audio system settle
            import time

            time.sleep(1.5)

            # Print the override message
            print(f"\n[AGENT] {override_message}")

            # Generate and play the override message audio
            try:
                import tempfile
                import subprocess
                import platform

                settings = get_settings()

                # Get the ElevenLabs client
                client = ElevenLabs(api_key=settings.elevenlabs_api_key)

                # Generate audio using the text_to_speech module
                print(f"[GALILEO PROTECT] Generating audio for override message...")
                audio_generator = client.text_to_speech.convert(
                    text=override_message,
                    voice_id="cjVigY5qzO86Huf0OWal",  # Eric voice ID
                    model_id="eleven_turbo_v2",
                    output_format="mp3_22050_32",  # Lower quality to match conversational audio
                )

                # Save audio to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    for chunk in audio_generator:
                        f.write(chunk)
                    temp_file = f.name

                # Play using system's default audio player
                print(f"[GALILEO PROTECT] Playing override message...")
                system = platform.system()
                if system == "Darwin":  # macOS
                    subprocess.run(["afplay", temp_file], check=True)
                elif system == "Windows":
                    os.startfile(temp_file)
                else:  # Linux
                    subprocess.run(["xdg-open", temp_file], check=True)

                # Clean up
                os.unlink(temp_file)

                print(f"[GALILEO PROTECT] Override message delivered via audio")

            except Exception as e:
                print(f"[GALILEO PROTECT] Failed to generate or play audio: {e}")
                print(f"[GALILEO PROTECT] Message was displayed as text above")
                import traceback

                traceback.print_exc()

            # Log the override message to Galileo as an agent turn
            # This ensures it shows up in the trace
            galileo.log_agent_turn(override_message)

            # End the conversation
            print("[GALILEO PROTECT] Ending conversation session...")
            galileo.end_conversation()
            print("[INFO] Conversation ended - logs sent to Galileo")
            raise SystemExit("Call terminated by guardrail")
        else:
            # No override message, just end immediately
            if _conversation:
                print("[GALILEO PROTECT] Ending session due to guardrail violation...")
                _conversation.end_session()
                galileo.end_conversation()
                raise SystemExit("Call terminated by guardrail")


def on_mode_change(mode: dict) -> None:
    """Called when conversation mode changes (speaking/listening)."""
    print(f"[MODE] {mode}")


def run_voice_conversation(use_headphones: bool = True):
    """Run a voice conversation with microphone input and speaker output.

    Args:
        use_headphones: If True, plays audio through speakers.
                       Set to False if not using headphones to avoid feedback loop.
    """
    settings = get_settings()

    # Initialize ElevenLabs client
    client = ElevenLabs(api_key=settings.elevenlabs_api_key)

    # Initialize Galileo and start conversation trace
    galileo = _get_galileo()
    session_id = str(uuid.uuid4())
    galileo.start_conversation(session_id)

    print("\n" + "=" * 60)
    print("ElevenLabs Voice POC - Voice Mode + Galileo")
    print(f"Session ID: {session_id}")
    if use_headphones:
        print("*** USE HEADPHONES to avoid audio feedback loop ***")
    else:
        print("*** Silent mode - no audio playback ***")
    print("Speak into your microphone to talk to the agent")
    print("Press Ctrl+C to end the session")
    print("=" * 60 + "\n")

    global _conversation

    # Create conversation with audio interface
    conversation = Conversation(
        client=client,
        agent_id=settings.elevenlabs_agent_id,
        requires_auth=True,  # We're using API key auth
        # Required: audio interface for mic/speaker
        audio_interface=DefaultAudioInterface(),
        # Callbacks for monitoring - connected to Galileo
        callback_agent_response=on_agent_response,
        callback_user_transcript=on_user_transcript,
        # callback_mode_change=on_mode_change,  # Optional
    )

    _conversation = conversation

    # Start the conversation (blocking)
    print("[INFO] Starting conversation... Speak now!")
    conversation.start_session()

    # Wait for conversation to end
    try:
        conversation.wait_for_session_end()
    except KeyboardInterrupt:
        print("\n[INFO] Ending conversation...")
        conversation.end_session()

    # End Galileo trace and flush logs
    galileo.end_conversation()
    print("[INFO] Conversation ended - logs sent to Galileo")


if __name__ == "__main__":
    run_voice_conversation()
