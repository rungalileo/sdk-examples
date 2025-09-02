import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Healthcare Support Portal - Patient Service"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = "0.0.0.0"
    port: int = 8002

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare",
    )

    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")

    # Oso Configuration
    oso_url: str = os.getenv("OSO_URL", "http://localhost:8080")
    oso_auth: str = os.getenv("OSO_AUTH", "e_0123456789_12345_osotesttoken01xiIn")

    class Config:
        env_file = ".env"


settings = Settings()
