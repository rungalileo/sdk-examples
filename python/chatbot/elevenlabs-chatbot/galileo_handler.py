"""Galileo Handler for ElevenLabs Voice Chatbot

Provides observability for AI applications by capturing:
- Sessions: Group related conversations (e.g., a user's chat session)
- Traces: Individual request-response cycles within a session
- Spans: Detailed steps within a trace (e.g., LLM calls, tool use)

This allows you to monitor conversation quality, debug issues, and
analyze patterns in your AI application.
"""

import os
from typing import Optional

from galileo import GalileoLogger, Message, MessageRole


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
