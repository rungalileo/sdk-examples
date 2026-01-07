"""Main entry point for the ElevenLabs Voice POC."""

import asyncio
import sys

from config import get_settings
from elevenlabs_monitor import ElevenLabsMonitor


def main() -> None:
    """Run the ElevenLabs voice conversation monitor."""
    try:
        settings = get_settings()
    except Exception as e:
        print(f"[ERROR] Failed to load configuration: {e}")
        print("\nMake sure you have a .env file with:")
        print("  ELEVENLABS_API_KEY=your-api-key")
        print("  ELEVENLABS_AGENT_ID=your-agent-id")
        print("  GALILEO_API_KEY=your-galileo-api-key")
        sys.exit(1)

    # Create monitor instance
    monitor = ElevenLabsMonitor(
        api_key=settings.elevenlabs_api_key,
        agent_id=settings.elevenlabs_agent_id,
        ws_url=settings.elevenlabs_ws_url,
    )

    # Run the interactive session
    try:
        asyncio.run(monitor.run_interactive())
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")


if __name__ == "__main__":
    main()
