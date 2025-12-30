"""Configuration management for the ElevenLabs Voice POC."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ElevenLabs Configuration
    elevenlabs_api_key: str
    elevenlabs_agent_id: str

    # WebSocket monitoring endpoint
    elevenlabs_ws_url: str = "wss://api.elevenlabs.io/v1/convai/conversation"

    # Galileo Configuration
    galileo_api_key: str = ""
    galileo_console_url: str = "http://localhost:3000"  # Local Galileo instance
    galileo_project_name: str = "elevenlabs-voice-poc"
    galileo_log_stream: str = "voice-conversations"

    galileo_protect_enabled: bool = True
    galileo_protect_stage_id: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
