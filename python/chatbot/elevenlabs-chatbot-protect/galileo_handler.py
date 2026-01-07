"""Galileo integration for logging and runtime protection.

Demonstrates how to use GalileoLogger and invoke_protect with a voice chatbot.
"""

import os
from typing import Optional

from galileo import GalileoLogger, Message, MessageRole, invoke_protect, ExecutionStatus
from galileo_core.schemas.protect.payload import Payload

from config import get_settings


class GalileoHandler:
    """Handles Galileo logging and Protect guardrails for voice conversations."""

    def __init__(self):
        self.settings = get_settings()
        self._logger: Optional[GalileoLogger] = None
        self._protect_enabled = False
        self._session_id: Optional[str] = None
        self._turn_count = 0

        # Set environment variables for Galileo SDK
        os.environ["GALILEO_CONSOLE_URL"] = self.settings.galileo_console_url
        os.environ["GALILEO_API_KEY"] = self.settings.galileo_api_key

        self._init_logger()
        self._init_protect()

    def _init_logger(self):
        """Initialize Galileo Logger."""
        try:
            self._logger = GalileoLogger(
                project=self.settings.galileo_project_name,
                log_stream=self.settings.galileo_log_stream,
            )
            print(f"[GALILEO] Logger initialized for project: {self.settings.galileo_project_name}")
        except Exception as e:
            print(f"[GALILEO] Logger init failed: {e}")

    def _init_protect(self):
        """Initialize Galileo Protect if configured."""
        if self.settings.galileo_protect_enabled and self.settings.galileo_protect_stage_id:
            self._protect_enabled = True
            print(f"[GALILEO] Protect enabled with stage: {self.settings.galileo_protect_stage_id}")
        else:
            print("[GALILEO] Protect disabled")

    def start_conversation(self, session_id: str):
        """Start a new conversation session."""
        self._session_id = session_id
        self._turn_count = 0

        if self._logger:
            self._logger.start_session(name=f"Voice-{session_id[:8]}", external_id=session_id)
            print(f"[GALILEO] Started session: {session_id[:8]}")

    def check_input_guardrail(self, text: str) -> dict:
        """Check user input against Protect guardrails.

        Returns: {"blocked": bool, "reason": str|None, "override_message": str|None}
        """
        if not self._protect_enabled:
            return {"blocked": False, "reason": None, "override_message": None}

        try:
            payload = Payload(input=text)
            result = invoke_protect(
                payload=payload,
                stage_id=self.settings.galileo_protect_stage_id,
                project_name=self.settings.galileo_project_name,
            )

            if result and result.status == ExecutionStatus.triggered:
                override_message = None
                if hasattr(result, "action_result") and isinstance(result.action_result, dict):
                    if result.action_result.get("type") == "OVERRIDE":
                        override_message = result.action_result.get("value")

                return {"blocked": True, "reason": "Input guardrail triggered", "override_message": override_message}

        except Exception as e:
            print(f"[GALILEO] Protect error: {e}")

        return {"blocked": False, "reason": None, "override_message": None}

    def check_output_guardrail(self, text: str) -> dict:
        """Check agent output against Protect guardrails.

        Returns: {"blocked": bool, "reason": str|None}
        """
        if not self._protect_enabled:
            return {"blocked": False, "reason": None}

        try:
            payload = Payload(output=text)
            result = invoke_protect(
                payload=payload,
                stage_id=self.settings.galileo_protect_stage_id,
                project_name=self.settings.galileo_project_name,
            )

            if result and result.status == ExecutionStatus.triggered:
                return {"blocked": True, "reason": "Output guardrail triggered"}

        except Exception as e:
            print(f"[GALILEO] Protect error: {e}")

        return {"blocked": False, "reason": None}

    def log_user_turn(self, transcript: str) -> dict:
        """Log user input and check input guardrails.

        Returns: {"blocked": bool, "reason": str|None, "override_message": str|None}
        """
        self._turn_count += 1
        self._last_user_input = transcript

        # Start a new trace for this turn
        if self._logger:
            try:
                self._logger.start_trace(input=transcript, name=f"Turn-{self._turn_count}")
            except Exception as e:
                print(f"[GALILEO] Trace start error: {e}")

        # Check input guardrail
        return self.check_input_guardrail(transcript)

    def log_agent_turn(self, response: str) -> dict:
        """Log agent response and check output guardrails.

        Returns: {"blocked": bool, "reason": str|None}
        """
        # Log the LLM span
        if self._logger:
            try:
                user_input = getattr(self, "_last_user_input", "")
                self._logger.add_llm_span(
                    input=user_input,
                    output=Message(content=response, role=MessageRole.assistant),
                    model="elevenlabs-agent",
                )
                self._logger.conclude(output=response)
                self._logger.flush()
            except Exception as e:
                print(f"[GALILEO] Logging error: {e}")

        # Check output guardrail
        return self.check_output_guardrail(response)

    def end_conversation(self):
        """End the conversation and cleanup."""
        if self._logger:
            try:
                self._logger.flush()
                self._logger.clear_session()
                print(f"[GALILEO] Session ended ({self._turn_count} turns)")
            except Exception as e:
                print(f"[GALILEO] Cleanup error: {e}")

        self._session_id = None
        self._turn_count = 0


# Singleton instance
_handler: Optional[GalileoHandler] = None


def get_galileo_handler() -> GalileoHandler:
    """Get or create the Galileo handler singleton."""
    global _handler
    if _handler is None:
        _handler = GalileoHandler()
    return _handler
