"""ElevenLabs WebSocket client for conversation monitoring."""

import asyncio
import json
from dataclasses import dataclass
from typing import Callable, Optional
import websockets
from websockets.exceptions import ConnectionClosed


@dataclass
class ConversationEvent:
    """Represents a conversation event from ElevenLabs."""

    event_type: str
    data: dict

    @property
    def transcript(self) -> Optional[str]:
        """Get transcript text for user_transcript events."""
        if self.event_type == "user_transcript":
            # Check nested structure first
            event_data = self.data.get("user_transcript_event", {})
            return event_data.get("user_transcript", self.data.get("user_transcript", ""))
        return None

    @property
    def response(self) -> Optional[str]:
        """Get response text for agent_response events."""
        if self.event_type == "agent_response":
            # Check nested structure first
            event_data = self.data.get("agent_response_event", {})
            return event_data.get("agent_response", self.data.get("agent_response", ""))
        return None


class ElevenLabsMonitor:
    """WebSocket client for monitoring ElevenLabs conversations."""

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        ws_url: str = "wss://api.elevenlabs.io/v1/convai/conversation",
    ):
        self.api_key = api_key
        self.agent_id = agent_id
        self.ws_url = f"{ws_url}?agent_id={agent_id}"
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._running = False

        # Event callbacks
        self.on_user_transcript: Optional[Callable[[str], None]] = None
        self.on_agent_response: Optional[Callable[[str], None]] = None
        self.on_conversation_start: Optional[Callable[[dict], None]] = None
        self.on_conversation_end: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None

    async def connect(self) -> None:
        """Establish WebSocket connection to ElevenLabs."""
        headers = {"xi-api-key": self.api_key}
        print(f"[DEBUG] Connecting to: {self.ws_url}")
        self.ws = await websockets.connect(
            self.ws_url,
            additional_headers=headers,
            ping_interval=20,
            ping_timeout=10,
        )
        self._running = True
        print("[DEBUG] WebSocket connected, sending init message...")

        # Send initialization message (minimal - let agent use its configured settings)
        init_msg = {
            "type": "conversation_initiation_client_data",
        }
        await self.ws.send(json.dumps(init_msg))
        print("[DEBUG] Init message sent")

    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        self._running = False
        if self.ws:
            await self.ws.close()
            self.ws = None

    async def send_text_message(self, text: str) -> None:
        """Send a text message to the agent (simulates user input)."""
        if not self.ws:
            raise RuntimeError("Not connected")

        msg = {"type": "user_message", "message": text}
        await self.ws.send(json.dumps(msg))

    async def _handle_message(self, message: str) -> None:
        """Process incoming WebSocket message."""
        try:
            data = json.loads(message)
            event_type = data.get("type", "unknown")

            # Debug: print raw message for troubleshooting
            print(f"[DEBUG RAW] {json.dumps(data, indent=2)[:500]}")

            # Create event object
            event = ConversationEvent(event_type=event_type, data=data)

            # Handle different event types
            if event_type == "conversation_initiation_metadata":
                # conversation_id may be nested or at top level
                meta = data.get("conversation_initiation_metadata_event", data)
                conv_id = meta.get("conversation_id", data.get("conversation_id", "N/A"))
                print(f"[INIT] Conversation started - ID: {conv_id}")
                if self.on_conversation_start:
                    self.on_conversation_start(data)

            elif event_type == "user_transcript":
                transcript = event.transcript or ""
                print(f"[USER] {transcript}")
                if self.on_user_transcript:
                    self.on_user_transcript(transcript)

            elif event_type == "agent_response":
                response = event.response or ""
                print(f"[AGENT] {response}")
                if self.on_agent_response:
                    self.on_agent_response(response)

            elif event_type == "agent_response_correction":
                # Agent corrected its response
                corrected = data.get("agent_response_correction", "")
                print(f"[AGENT CORRECTION] {corrected}")

            elif event_type == "audio":
                # Audio chunk - skip for text-only monitoring
                pass

            elif event_type == "ping":
                # Respond to ping with pong (event_id is nested in ping_event)
                ping_event = data.get("ping_event", {})
                event_id = ping_event.get("event_id", data.get("event_id"))
                pong = {"type": "pong", "event_id": event_id}
                if self.ws:
                    await self.ws.send(json.dumps(pong))
                    print(f"[DEBUG] Sent pong for event_id: {event_id}")

            elif event_type == "interruption":
                print("[EVENT] User interrupted agent")

            elif event_type == "error":
                error_msg = data.get("message", "Unknown error")
                print(f"[ERROR] {error_msg}")

            else:
                # Log other event types for debugging
                print(f"[DEBUG] Event: {event_type}")

        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse message: {e}")

    async def listen(self) -> None:
        """Listen for messages from WebSocket."""
        if not self.ws:
            raise RuntimeError("Not connected")

        try:
            async for message in self.ws:
                if not self._running:
                    break
                await self._handle_message(message)

        except ConnectionClosed as e:
            print(f"[INFO] Connection closed: {e.reason}")
            if self.on_conversation_end:
                self.on_conversation_end()

        except Exception as e:
            print(f"[ERROR] WebSocket error: {e}")
            if self.on_error:
                self.on_error(e)

    async def run_interactive(self) -> None:
        """Run an interactive text conversation session."""
        await self.connect()

        # Start listening in background
        listen_task = asyncio.create_task(self.listen())

        print("\n" + "=" * 60)
        print("ElevenLabs Voice POC - Interactive Mode")
        print("Type your message and press Enter to send")
        print("Type 'quit' or 'exit' to end the session")
        print("=" * 60 + "\n")

        try:
            while self._running:
                # Read user input (in a non-blocking way)
                user_input = await asyncio.get_event_loop().run_in_executor(None, input, "You: ")

                if user_input.lower() in ("quit", "exit"):
                    break

                if user_input.strip():
                    await self.send_text_message(user_input)

        except (KeyboardInterrupt, EOFError):
            print("\n[INFO] Session interrupted")

        finally:
            self._running = False
            listen_task.cancel()
            await self.disconnect()
            print("[INFO] Disconnected")
