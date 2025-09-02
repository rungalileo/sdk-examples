import sqlalchemy_oso_cloud
from common.migration_check import require_migrations_current
from common.models import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import auth, users

# Initialize SQLAlchemy Oso Cloud with registry and server settings
sqlalchemy_oso_cloud.init(
    Base.registry,
    url=settings.oso_url,
    api_key=settings.oso_auth,
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Authentication and user management service",
    version="0.1.0",
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])


@app.on_event("startup")
async def startup_event():
    """Verify migrations and start service"""
    # Verify database migrations are current
    require_migrations_current()
    print(f"🚀 {settings.app_name} started on port {settings.port}")


@app.get("/")
async def root():
    return {"service": "auth_service", "status": "healthy", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Make Oso Cloud instance available to routes
app.state.oso_sqlalchemy = sqlalchemy_oso_cloud
