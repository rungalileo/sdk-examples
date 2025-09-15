import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "Healthcare Support Portal - RAG Service"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = "0.0.0.0"
    port: int = 8003

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare",
    )

    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"

    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_context_length: int = 8000
    similarity_threshold: float = 0.3
    max_results: int = 5

    # Oso Configuration
    oso_url: str = os.getenv("OSO_URL", "http://localhost:8080")
    oso_auth: str = os.getenv("OSO_AUTH", "e_0123456789_12345_osotesttoken01xiIn")

    # Galileo 2.0 Observability Configuration
    galileo_enabled: bool = os.getenv("GALILEO_ENABLED", "true").lower() == "true"
    galileo_api_key: str = os.getenv("GALILEO_API_KEY", "")
    galileo_project_name: str = os.getenv("GALILEO_PROJECT_NAME", "healthcare-rag")
    galileo_environment: str = os.getenv("GALILEO_ENVIRONMENT", "development")

    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")  # json or console

    class Config:
        env_file = ".env"
        # Explicitly ignore extra fields to prevent OpenTelemetry/Prometheus
        # env vars from being loaded
        extra = "ignore"


settings = Settings()
