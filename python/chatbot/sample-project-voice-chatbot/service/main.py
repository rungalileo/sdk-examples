"""FastAPI service for Galileo integration.

This service handles ALL Galileo logging from the Next.js app:
- Session management
- Conversation turn logging
- Protect span logging (for proper Protect Status in UI)

By having Python handle all logging, protect spans are in the same trace
as conversation turns, which is required for Protect Status to display correctly.
"""

# Load environment variables from .env file (must be before other imports)
from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Galileo imports
from galileo import GalileoLogger, invoke_protect, ExecutionStatus, Message, MessageRole
from galileo_core.schemas.protect.payload import Payload


# Pydantic models for request/response
class ProtectRequest(BaseModel):
    session_id: str
    input_text: Optional[str] = None
    output_text: Optional[str] = None
    stage_id: str
    project_name: str
    metadata: Optional[Dict[str, Any]] = None


class TriggeredRule(BaseModel):
    metric: str
    value: Any  # Can be float (toxicity) or list (PII)
    threshold: Any  # Can be float (toxicity) or list (PII)
    operator: str


class ProtectResponse(BaseModel):
    blocked: bool
    status: str
    triggered_rules: List[TriggeredRule] = []
    override_message: Optional[str] = None
    raw_result: Optional[Dict[str, Any]] = None


class ConversationTurnRequest(BaseModel):
    session_id: str
    user_transcript: str
    agent_response: str
    turn_number: int
    latency_ms: float
    conversation_context: List[Dict[str, str]] = []
    check_guardrails: bool = True
    stage_id: Optional[str] = None
    project_name: str


class ConversationTurnResponse(BaseModel):
    success: bool
    blocked: bool = False
    override_message: Optional[str] = None
    input_guardrail: Optional[ProtectResponse] = None
    output_guardrail: Optional[ProtectResponse] = None


# Session manager for Galileo loggers
class SessionManager:
    """Manages Galileo logger sessions."""

    def __init__(self):
        self._loggers: Dict[str, GalileoLogger] = {}
        self._active_traces: Dict[str, bool] = {}

    def get_or_create_logger(
        self,
        session_id: str,
        project_name: str,
        log_stream: str = "voice-conversations",
    ) -> GalileoLogger:
        """Get existing logger or create a new one."""
        if session_id not in self._loggers:
            logger = GalileoLogger(
                project=project_name,
                log_stream=log_stream,
            )
            logger.start_session(
                name=f"Voice-{session_id[:8]}",
                external_id=session_id,
            )
            self._loggers[session_id] = logger
            self._active_traces[session_id] = False
            print(f"[GALILEO] Created session: {session_id}")

        return self._loggers[session_id]

    def has_active_trace(self, session_id: str) -> bool:
        return self._active_traces.get(session_id, False)

    def set_active_trace(self, session_id: str, active: bool):
        self._active_traces[session_id] = active

    def end_session(self, session_id: str):
        """End and remove a session."""
        if session_id in self._loggers:
            logger = self._loggers[session_id]
            try:
                if self._active_traces.get(session_id):
                    logger.conclude(output="Session ended")
                logger.flush()
                logger.clear_session()
            except Exception as e:
                print(f"[GALILEO] Error ending session: {e}")
            finally:
                del self._loggers[session_id]
                if session_id in self._active_traces:
                    del self._active_traces[session_id]
                print(f"[GALILEO] Ended session: {session_id}")


# Global session manager
session_manager = SessionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("[GALILEO] Python Protect service starting...")

    # Verify environment variables
    required_vars = ["GALILEO_API_KEY", "GALILEO_CONSOLE_URL"]
    for var in required_vars:
        if not os.environ.get(var):
            print(f"[WARNING] {var} not set")

    yield

    # Shutdown - clean up all sessions
    print("[GALILEO] Shutting down, cleaning up sessions...")
    for session_id in list(session_manager._loggers.keys()):
        session_manager.end_session(session_id)


app = FastAPI(
    title="Galileo Protect Service",
    description="Python microservice for Galileo Protect integration with proper span logging",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for Next.js app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your Next.js domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "galileo-protect",
        "active_sessions": len(session_manager._loggers),
    }


def _invoke_and_parse_protect(
    text: str,
    is_input: bool,
    stage_id: str,
    project_name: str,
    metadata: Optional[Dict[str, Any]] = None
) -> tuple[Any, Optional[Any], "ProtectResponse"]:
    """Helper to invoke protect and parse the result."""
    # Always use 'input' field for toxicity checks since input_toxicity metric
    # requires the text to be in the 'input' field, regardless of whether
    # we're checking user input or agent output
    payload_data = {"input": text}
    if metadata:
        payload_data["metadata"] = metadata

    payload = Payload(**payload_data)

    print(f"[DEBUG] Invoking protect with stage_id={stage_id}, project={project_name}")
    print(f"[DEBUG] Payload: {payload_data}")

    try:
        protect_result = invoke_protect(
            payload=payload,
            stage_id=stage_id,
            project_name=project_name,
        )
        print(f"[DEBUG] Protect result: {protect_result}")
        print(f"[DEBUG] Protect result type: {type(protect_result)}")
        if protect_result:
            print(f"[DEBUG] Protect result status: {protect_result.status}")
            print(f"[DEBUG] Protect result dir: {[attr for attr in dir(protect_result) if not attr.startswith('_')]}")
    except Exception as e:
        print(f"[ERROR] invoke_protect failed: {e}")
        import traceback
        traceback.print_exc()
        protect_result = None

    blocked = False
    triggered_rules = []
    override_message = None
    status = "not_triggered"

    if protect_result:
        if protect_result.status == ExecutionStatus.triggered:
            blocked = True
            status = "triggered"

        if hasattr(protect_result, 'action_result') and protect_result.action_result:
            action_result = protect_result.action_result
            if isinstance(action_result, dict) and action_result.get('type') == 'OVERRIDE':
                override_message = action_result.get('value')

        if hasattr(protect_result, 'ruleset_results') and protect_result.ruleset_results:
            for ruleset_result in protect_result.ruleset_results:
                if 'rule_results' in ruleset_result:
                    for rule_result in ruleset_result['rule_results']:
                        if rule_result.get('status') == 'TRIGGERED':
                            # Handle different value types (float for toxicity, list for PII)
                            raw_value = rule_result.get('value', 0)
                            raw_threshold = rule_result.get('target_value', 0)
                            triggered_rules.append(TriggeredRule(
                                metric=rule_result.get('metric', 'unknown'),
                                value=raw_value,
                                threshold=raw_threshold,
                                operator=rule_result.get('operator', 'N/A'),
                            ))

    return payload, protect_result, ProtectResponse(
        blocked=blocked,
        status=status,
        triggered_rules=triggered_rules,
        override_message=override_message,
    )


@app.post("/log-conversation-turn", response_model=ConversationTurnResponse)
async def log_conversation_turn(request: ConversationTurnRequest):
    """
    Log a conversation turn with protect spans in the SAME trace.

    This is the main endpoint that Next.js should use for logging.
    It handles:
    1. Starting/continuing a trace
    2. Input guardrail check with protect span
    3. LLM response span
    4. Output guardrail check with protect span
    5. Concluding and flushing the trace
    """
    try:
        # Debug logging
        print(f"[DEBUG] Request received:")
        print(f"  session_id: {request.session_id}")
        print(f"  user_transcript: {request.user_transcript[:50] if request.user_transcript else 'None'}...")
        print(f"  check_guardrails: {request.check_guardrails}")
        print(f"  stage_id: {request.stage_id}")
        print(f"  project_name: {request.project_name}")

        log_stream = os.environ.get("GALILEO_LOG_STREAM", "voice-conversations")
        logger = session_manager.get_or_create_logger(
            session_id=request.session_id,
            project_name=request.project_name,
            log_stream=log_stream,
        )

        # Conclude previous trace if active
        if session_manager.has_active_trace(request.session_id):
            try:
                logger.conclude(output="Turn completed")
            except:
                pass

        # Start new trace for this turn
        logger.start_trace(
            input=request.user_transcript,
            name=f"Turn-{request.turn_number}",
            metadata={
                "session_id": request.session_id,
                "turn_number": str(request.turn_number),
                "source": "elevenlabs-voice",
            },
        )
        session_manager.set_active_trace(request.session_id, True)

        blocked = False
        override_message = None
        input_guardrail_response = None
        output_guardrail_response = None

        # Check input guardrail
        if request.check_guardrails and request.stage_id:
            payload, protect_result, input_guardrail_response = _invoke_and_parse_protect(
                text=request.user_transcript,
                is_input=True,
                stage_id=request.stage_id,
                project_name=request.project_name,
                metadata={"role": "user"},
            )

            # Add protect span to THIS trace
            if protect_result:
                try:
                    logger.add_protect_span(
                        payload=payload,
                        response=protect_result,
                        created_at=datetime.now(),
                        metadata={"stage": "input_guardrail"},
                        status_code=200,
                    )
                    print(f"[GALILEO] Added input protect span: {input_guardrail_response.status}")
                except Exception as e:
                    print(f"[ERROR] Failed to add input protect span: {e}")
                    import traceback
                    traceback.print_exc()

            if input_guardrail_response.blocked:
                blocked = True
                override_message = input_guardrail_response.override_message

        # Add LLM span for agent response
        output_message = Message(
            content=override_message if blocked else request.agent_response,
            role=MessageRole.assistant,
        )

        logger.add_llm_span(
            input=request.conversation_context if request.conversation_context else request.user_transcript,
            output=output_message,
            model="elevenlabs-agent",
            name="Agent_Response",
            metadata={
                "latency_ms": str(int(request.latency_ms)),
                "blocked": str(blocked),
            },
        )

        # Check output guardrail (only if input wasn't blocked)
        if request.check_guardrails and request.stage_id and not blocked:
            payload, protect_result, output_guardrail_response = _invoke_and_parse_protect(
                text=request.agent_response,
                is_input=False,
                stage_id=request.stage_id,
                project_name=request.project_name,
                metadata={"role": "assistant"},
            )

            # Add protect span to THIS trace
            if protect_result:
                try:
                    logger.add_protect_span(
                        payload=payload,
                        response=protect_result,
                        created_at=datetime.now(),
                        metadata={"stage": "output_guardrail"},
                        status_code=200,
                    )
                    print(f"[GALILEO] Added output protect span: {output_guardrail_response.status}")
                except Exception as e:
                    print(f"[ERROR] Failed to add output protect span: {e}")
                    import traceback
                    traceback.print_exc()

            if output_guardrail_response.blocked:
                blocked = True
                override_message = output_guardrail_response.override_message

        # Conclude and flush
        final_output = override_message if blocked else request.agent_response
        logger.conclude(output=final_output)
        logger.flush()
        session_manager.set_active_trace(request.session_id, False)

        print(f"[GALILEO] Turn {request.turn_number} logged (blocked={blocked})")

        return ConversationTurnResponse(
            success=True,
            blocked=blocked,
            override_message=override_message,
            input_guardrail=input_guardrail_response,
            output_guardrail=output_guardrail_response,
        )

    except Exception as e:
        print(f"[ERROR] log_conversation_turn failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/invoke-protect", response_model=ProtectResponse)
async def invoke_protect_endpoint(request: ProtectRequest):
    """
    Standalone protect invocation (without trace logging).
    Use /log-conversation-turn for full logging with protect spans.
    """
    try:
        _, _, response = _invoke_and_parse_protect(
            text=request.input_text or request.output_text or "",
            is_input=bool(request.input_text),
            stage_id=request.stage_id,
            project_name=request.project_name,
            metadata=request.metadata,
        )
        return response

    except Exception as e:
        print(f"[ERROR] invoke_protect failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/end-session/{session_id}")
async def end_session(session_id: str):
    """End a session and clean up resources."""
    session_manager.end_session(session_id)
    return {"status": "ended", "session_id": session_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
