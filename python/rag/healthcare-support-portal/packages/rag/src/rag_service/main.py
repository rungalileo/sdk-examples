import sys
from pathlib import Path

# Add the common package to Python path
common_path = Path(__file__).parent.parent.parent.parent / "common" / "src"
sys.path.insert(0, str(common_path))

import sqlalchemy_oso_cloud
from common.migration_check import require_migrations_current
from common.models import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from galileo.openai import openai

from .config import settings
from .observability import initialize_observability, ObservabilityMiddleware, logger
from .routers import chat, documents

# Set OpenAI API key
openai.api_key = settings.openai_api_key

# Initialize SQLAlchemy Oso Cloud with registry and server settings
# Add error handling for development environments where OSO might not be available
try:
    sqlalchemy_oso_cloud.init(Base.registry, url=settings.oso_url, api_key=settings.oso_auth)
    print(f"✅ OSO Cloud initialized: {settings.oso_url}")
except Exception as e:
    print(f"⚠️  OSO Cloud initialization failed: {e}")
    print("🔧 Authorization will be disabled - use for development only!")
    # You may want to set a flag here to disable authorization checks

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="RAG service with vector search and AI-powered responses",
    version="0.1.0",
    debug=settings.debug,
)

# Add observability middleware
app.add_middleware(ObservabilityMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])


@app.on_event("startup")
async def startup_event():
    """Verify migrations and start service"""
    try:
        # Initialize observability components
        initialize_observability()

        # Verify database migrations are current
        require_migrations_current()

        logger.info(f"🚀 {settings.app_name} started successfully", port=settings.port, galileo_enabled=settings.galileo_enabled)

    except Exception as e:
        logger.error(f"Failed to start {settings.app_name}", error=str(e))
        raise


@app.get("/")
async def root():
    return {"service": "rag_service", "status": "healthy", "version": "0.1.0", "observability": {"galileo_enabled": settings.galileo_enabled}}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/observability")
async def observability_status():
    """Get observability configuration status"""
    return {
        "galileo": {"enabled": settings.galileo_enabled, "project": settings.galileo_project_name, "environment": settings.galileo_environment},
        "logging": {"level": settings.log_level, "format": settings.log_format},
    }


# Make Oso Cloud instance and settings available to routes
app.state.oso_sqlalchemy = sqlalchemy_oso_cloud
app.state.settings = settings
