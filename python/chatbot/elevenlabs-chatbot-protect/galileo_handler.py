"""Galileo integration for logging, tracing.

Uses the galileo.GalileoLogger API which auto-creates projects in Galileo.
Enables context_adherence metric on the log stream.
"""

import os
import time
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime

from galileo import GalileoScorers, invoke_protect, ExecutionStatus
from galileo.log_streams import enable_metrics
from galileo_core.schemas.protect.payload import Payload

from config import get_settings


# Keywords that trigger call disruption (simulating Galileo guardrails)
BLOCKED_KEYWORDS = ["uss enterprise"]


@dataclass
class ConversationTrace:
    """Tracks a single conversation session for Galileo logging."""

    session_id: str
    start_time: datetime = field(default_factory=datetime.now)
    start_timestamp: float = field(default_factory=time.time)
    turns: List[Dict] = field(default_factory=list)
    active_trace: bool = False
    conversation_context: List[Dict] = field(default_factory=list)

    # Metrics tracking
    last_user_turn_time: Optional[float] = None  # For latency calculation
    latencies_ms: List[float] = field(default_factory=list)  # Response latencies
    user_char_count: int = 0
    agent_char_count: int = 0


class GalileoHandler:
    """Handles Galileo logging

    Uses GalileoLogger from the galileo package which auto-creates projects.
    Captures comprehensive metrics for voice conversation analysis.
    """

    def __init__(self):
        self.settings = get_settings()
        self._galileo_client = None
        self._protect_enabled = False
        self._current_trace: Optional[ConversationTrace] = None

        # Set Galileo environment variables BEFORE importing galileo
        if self.settings.galileo_console_url:
            os.environ["GALILEO_CONSOLE_URL"] = self.settings.galileo_console_url
        if self.settings.galileo_api_key:
            os.environ["GALILEO_API_KEY"] = self.settings.galileo_api_key

        self._init_observe()
        self._init_protect()

    def _init_observe(self):
        """Initialize Galileo Logger for logging/tracing."""
        try:
            from galileo import GalileoLogger

            init_kwargs = {}
            if self.settings.galileo_project_name:
                init_kwargs["project"] = self.settings.galileo_project_name
            if self.settings.galileo_log_stream:
                init_kwargs["log_stream"] = self.settings.galileo_log_stream

            self._galileo_client = GalileoLogger(**init_kwargs)
            print(f"[GALILEO] Logger initialized - Project: {self.settings.galileo_project_name}, Stream: {self.settings.galileo_log_stream}")

            # Enable context_adherence metric on the log stream
            enable_metrics(
                project_name=self.settings.galileo_project_name,
                log_stream_name=self.settings.galileo_log_stream,
                metrics=[GalileoScorers.context_adherence],
            )
            print(f"[GALILEO] Enabled metrics: context_adherence")
        except ImportError as e:
            print(f"[GALILEO] Warning: galileo package not installed, logging disabled: {e}")
        except Exception as e:
            print(f"[GALILEO] Warning: Could not initialize Logger: {e}")

    def _init_protect(self):
        """Initialize Galileo Protect for guardrails."""
        if not self.settings.galileo_protect_enabled:
            print("[GALILEO] Protect disabled via config")
            return

        if not self.settings.galileo_protect_stage_id:
            print("[GALILEO] Protect disabled - no stage_id configured")
            return

        if not self.settings.galileo_project_name:
            print("[GALILEO] Protect disabled - no project_name configured")
            return

        # No client initialization needed - invoke_protect is a function
        self._protect_enabled = True
        print(f"[GALILEO] Protect enabled - Stage: {self.settings.galileo_protect_stage_id}")

    def _calculate_metrics(self) -> Dict[str, str]:
        """Calculate session-level metrics."""
        if not self._current_trace:
            return {}

        trace = self._current_trace
        duration_sec = time.time() - trace.start_timestamp
        user_turns = sum(1 for t in trace.turns if t["role"] == "user")
        agent_turns = sum(1 for t in trace.turns if t["role"] == "assistant")

        avg_latency_ms = 0.0
        if trace.latencies_ms:
            avg_latency_ms = sum(trace.latencies_ms) / len(trace.latencies_ms)

        return {
            "duration_sec": f"{duration_sec:.2f}",
            "total_turns": str(len(trace.turns)),
            "user_turns": str(user_turns),
            "agent_turns": str(agent_turns),
            "avg_latency_ms": f"{avg_latency_ms:.0f}",
            "min_latency_ms": f"{min(trace.latencies_ms):.0f}" if trace.latencies_ms else "0",
            "max_latency_ms": f"{max(trace.latencies_ms):.0f}" if trace.latencies_ms else "0",
            "user_char_count": str(trace.user_char_count),
            "agent_char_count": str(trace.agent_char_count),
            "total_char_count": str(trace.user_char_count + trace.agent_char_count),
        }

    def start_conversation(self, session_id: str):
        """Start tracking a new conversation session."""
        self._current_trace = ConversationTrace(session_id=session_id)

        # Start a Galileo session for this conversation
        if self._galileo_client:
            try:
                session_name = f"ElevenLabs-{session_id[:8]}"
                # Start session - the session_id is automatically stored on the logger
                # NOTE: metadata is not supported on start_session - use trace metadata instead
                self._galileo_client.start_session(
                    name=session_name,
                    external_id=session_id,
                )
                # Session ID is now available on the logger instance
                print(f"[GALILEO] Started session: {session_name}")
                print(f"[GALILEO] Logger session_id: {self._galileo_client.session_id}")
            except Exception as e:
                print(f"[GALILEO] Failed to start session: {e}")
                import traceback

                traceback.print_exc()

        print(f"[GALILEO] Started conversation: {session_id}")

    def log_user_turn(self, transcript: str) -> dict:
        """Log a user turn (speech-to-text result) to Galileo.

        This starts a new trace for the conversation turn.

        Returns:
            dict with guardrail results if enabled, empty dict otherwise
        """
        result = {"blocked": False, "reason": None}
        current_time = time.time()

        # Simulate Galileo Protect API call (requires Enterprise for real invoke_protect)
        transcript_preview = transcript[:50] + "..." if len(transcript) > 50 else transcript
        print(f'[GALILEO PROTECT] invoke_protect(stage="voice-guardrails", input="{transcript_preview}")')

        # Check for blocked keywords (simulating what Galileo Protect would do)
        transcript_lower = transcript.lower()
        for keyword in BLOCKED_KEYWORDS:
            if keyword in transcript_lower:
                result["blocked"] = True
                result["reason"] = f"Blocked keyword detected: {keyword}"
                print(f'[GALILEO PROTECT] Response: status=TRIGGERED, action=BLOCK, rule="keyword:{keyword}"')
                return result

        print(f"[GALILEO PROTECT] Response: status=ALLOWED")

        if self._current_trace:
            # If there's an active trace, conclude it first
            if self._current_trace.active_trace and self._galileo_client:
                try:
                    last_response = "No response"
                    for turn in reversed(self._current_trace.turns):
                        if turn["role"] == "assistant":
                            last_response = turn["content"]
                            break
                    self._galileo_client.conclude(output=last_response)
                    self._current_trace.active_trace = False
                    print(f"[GALILEO] Concluded previous trace")
                except Exception as e:
                    print(f"[GALILEO] Failed to conclude previous trace: {e}")
                    import traceback

                    traceback.print_exc()

            # Track metrics
            self._current_trace.user_char_count += len(transcript)
            self._current_trace.last_user_turn_time = current_time

            # Add to conversation context
            self._current_trace.turns.append(
                {
                    "role": "user",
                    "content": transcript,
                    "timestamp": datetime.now().isoformat(),
                    "char_count": len(transcript),
                }
            )
            self._current_trace.conversation_context.append({"role": "user", "content": transcript})

            # Start a new trace for this user turn
            if self._galileo_client:
                try:
                    # Session persists automatically - no need to call set_session()
                    trace_num = sum(1 for t in self._current_trace.turns if t["role"] == "user")
                    self._galileo_client.start_trace(
                        input=transcript,
                        name=f"Turn-{trace_num}",
                        metadata={
                            "session_id": self._current_trace.session_id,
                            "turn_number": str(trace_num),
                            "role": "user",
                            "source": "elevenlabs-stt",
                            "char_count": str(len(transcript)),
                            "timestamp": datetime.now().isoformat(),
                        },
                    )
                    self._current_trace.active_trace = True
                    print(f"[GALILEO] Started trace {trace_num} in session {self._galileo_client.session_id}")
                except Exception as e:
                    print(f"[GALILEO] Failed to start trace: {e}")
                    import traceback

                    traceback.print_exc()

        # Run input guardrails if enabled
        if self._protect_enabled:
            try:
                payload = Payload(input=transcript, metadata={"role": "user"})

                protect_result = invoke_protect(
                    payload=payload,
                    stage_id=self.settings.galileo_protect_stage_id,
                    project_name=self.settings.galileo_project_name,
                )

                # Log the protect span to Galileo
                if self._galileo_client and self._current_trace.active_trace and protect_result:
                    try:
                        self._galileo_client.add_protect_span(
                            payload=payload,
                            response=protect_result,
                            created_at=datetime.now(),
                            metadata={
                                "session_id": self._current_trace.session_id,
                                "role": "user",
                                "stage": "input_guardrail",
                            },
                            status_code=200,
                        )
                        print(f"[GALILEO] Logged Protect span for input guardrail")
                    except Exception as e:
                        print(f"[GALILEO] Failed to log Protect span: {e}")

                if protect_result and protect_result.status == ExecutionStatus.triggered:
                    result["blocked"] = True

                    # Extract the override message to send to the user
                    override_message = None
                    if hasattr(protect_result, "action_result") and protect_result.action_result:
                        action_result = protect_result.action_result
                        if isinstance(action_result, dict) and action_result.get("type") == "OVERRIDE":
                            override_message = action_result.get("value")

                    # Also extract triggered metrics for logging
                    triggered_info = []
                    if hasattr(protect_result, "ruleset_results") and protect_result.ruleset_results:
                        for ruleset_result in protect_result.ruleset_results:
                            if "rule_results" in ruleset_result:
                                for rule_result in ruleset_result["rule_results"]:
                                    if rule_result.get("status") == "TRIGGERED":
                                        metric_name = rule_result.get("metric", "unknown")
                                        value = rule_result.get("value", "N/A")
                                        threshold = rule_result.get("target_value", "N/A")
                                        operator = rule_result.get("operator", "N/A")
                                        triggered_info.append(f"{metric_name}={value:.3f} (threshold: {operator} {threshold})")

                    result["reason"] = ", ".join(triggered_info) if triggered_info else "Unknown rule triggered"
                    result["override_message"] = override_message
                    print(f"[GALILEO PROTECT] Input blocked by: {result['reason']}")
                    if override_message:
                        print(f"[GALILEO PROTECT] Override message: {override_message}")
            except Exception as e:
                print(f"[GALILEO] Guardrail check failed: {e}")

        return result

    def log_agent_turn(self, response: str, model: str = "elevenlabs-agent") -> dict:
        """Log an agent turn (agent response) to Galileo.

        This adds an LLM span with latency metrics.

        Returns:
            dict with guardrail results if enabled, empty dict otherwise
        """
        result = {"blocked": False, "reason": None}
        current_time = time.time()
        latency_ms = 0.0

        if self._current_trace:
            # Calculate latency if we have a user turn timestamp
            if self._current_trace.last_user_turn_time:
                latency_ms = (current_time - self._current_trace.last_user_turn_time) * 1000
                self._current_trace.latencies_ms.append(latency_ms)

            # Track metrics
            self._current_trace.agent_char_count += len(response)

            self._current_trace.turns.append(
                {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat(),
                    "char_count": len(response),
                    "latency_ms": latency_ms,
                }
            )
            self._current_trace.conversation_context.append({"role": "assistant", "content": response})

            # Add LLM span for this response
            if self._galileo_client and self._current_trace.active_trace:
                try:
                    from galileo import Message, MessageRole

                    # Create output message
                    output_message = Message(content=response, role=MessageRole.assistant)

                    turn_num = sum(1 for t in self._current_trace.turns if t["role"] == "assistant")

                    self._galileo_client.add_llm_span(
                        input=self._current_trace.conversation_context.copy(),
                        output=output_message,
                        model=model,
                        name=f"Agent_Response_{turn_num}",
                        metadata={
                            "session_id": self._current_trace.session_id,
                            "turn_number": str(turn_num),
                            "latency_ms": f"{latency_ms:.0f}",
                            "char_count": str(len(response)),
                            "timestamp": datetime.now().isoformat(),
                        },
                    )

                    # Flush immediately so logs appear in real-time in Galileo
                    self._galileo_client.flush()
                    print(f"[GALILEO] Logged & flushed turn {turn_num} (latency: {latency_ms:.0f}ms, chars: {len(response)})")
                except Exception as e:
                    print(f"[GALILEO] Failed to add LLM span: {e}")

        # Run output guardrails if enabled
        if self._protect_enabled:
            try:
                payload = Payload(output=response, metadata={"role": "assistant"})

                protect_result = invoke_protect(
                    payload=payload,
                    stage_id=self.settings.galileo_protect_stage_id,
                    project_name=self.settings.galileo_project_name,
                )

                # Log the protect span to Galileo
                if self._galileo_client and self._current_trace.active_trace and protect_result:
                    try:
                        self._galileo_client.add_protect_span(
                            payload=payload,
                            response=protect_result,
                            created_at=datetime.now(),
                            metadata={
                                "session_id": self._current_trace.session_id,
                                "role": "assistant",
                                "stage": "output_guardrail",
                            },
                            status_code=200,
                        )
                        print(f"[GALILEO] Logged Protect span for output guardrail")
                    except Exception as e:
                        print(f"[GALILEO] Failed to log Protect span: {e}")

                if protect_result and protect_result.status == ExecutionStatus.triggered:
                    result["blocked"] = True

                    # Extract triggered metrics and values from ruleset_results
                    triggered_info = []
                    if hasattr(protect_result, "ruleset_results") and protect_result.ruleset_results:
                        for ruleset_result in protect_result.ruleset_results:
                            if "rule_results" in ruleset_result:
                                for rule_result in ruleset_result["rule_results"]:
                                    if rule_result.get("status") == "TRIGGERED":
                                        metric_name = rule_result.get("metric", "unknown")
                                        value = rule_result.get("value", "N/A")
                                        threshold = rule_result.get("target_value", "N/A")
                                        operator = rule_result.get("operator", "N/A")
                                        triggered_info.append(f"{metric_name}={value:.3f} (threshold: {operator} {threshold})")

                    result["reason"] = ", ".join(triggered_info) if triggered_info else "Unknown rule triggered"
                    print(f"[GALILEO PROTECT] Output flagged by: {result['reason']}")
            except Exception as e:
                print(f"[GALILEO] Guardrail check failed: {e}")

        return result

    def end_conversation(self):
        """End the current conversation and flush logs to Galileo with final metrics."""
        if not self._current_trace:
            return

        # Calculate final metrics
        metrics = self._calculate_metrics()

        # Conclude any active trace
        if self._galileo_client and self._current_trace.active_trace:
            try:
                last_response = "Conversation ended"
                for turn in reversed(self._current_trace.turns):
                    if turn["role"] == "assistant":
                        last_response = turn["content"]
                        break
                self._galileo_client.conclude(output=last_response)
                print(f"[GALILEO] Concluded final trace")
            except Exception as e:
                print(f"[GALILEO] Failed to conclude trace: {e}")
                import traceback

                traceback.print_exc()

        # Flush all logs to Galileo
        if self._galileo_client:
            try:
                print(f"[GALILEO] Flushing session {self._galileo_client.session_id}...")
                self._galileo_client.flush()
                print(f"[GALILEO] Flushed logs - {len(self._current_trace.turns)} turns logged")
            except Exception as e:
                print(f"[GALILEO] Failed to flush: {e}")
                import traceback

                traceback.print_exc()

        # Print metrics summary
        print(f"[GALILEO] Session metrics:")
        print(f"  - Duration: {metrics.get('duration_sec', '0')}s")
        print(f"  - Turns: {metrics.get('total_turns', '0')} (user: {metrics.get('user_turns', '0')}, agent: {metrics.get('agent_turns', '0')})")
        print(
            f"  - Avg latency: {metrics.get('avg_latency_ms', '0')}ms (min: {metrics.get('min_latency_ms', '0')}ms, max: {metrics.get('max_latency_ms', '0')}ms)"
        )
        print(
            f"  - Characters: {metrics.get('total_char_count', '0')} (user: {metrics.get('user_char_count', '0')}, agent: {metrics.get('agent_char_count', '0')})"
        )

        # Clear the session to properly end it
        if self._galileo_client and self._galileo_client.session_id:
            try:
                print(f"[GALILEO] Clearing session: {self._galileo_client.session_id}")
                self._galileo_client.clear_session()
                print(f"[GALILEO] Session cleared successfully")
            except Exception as e:
                print(f"[GALILEO] Failed to clear session: {e}")
                import traceback

                traceback.print_exc()

        self._current_trace = None


# Singleton instance
_handler: Optional[GalileoHandler] = None


def get_galileo_handler() -> GalileoHandler:
    """Get or create the Galileo handler singleton."""
    global _handler
    if _handler is None:
        _handler = GalileoHandler()
    return _handler
