#!/bin/bash
# packages/auth/run.sh

# Load .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set PYTHONPATH to include common package
export PYTHONPATH="../common/src:$PYTHONPATH"

# Set default environment variables if not already set
export SECRET_KEY="${SECRET_KEY:-your-secret-key-here}"
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare}"
export DEBUG="${DEBUG:-true}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8001}"
export ACCESS_TOKEN_EXPIRE_MINUTES="${ACCESS_TOKEN_EXPIRE_MINUTES:-30}"

echo "🔐 Starting Auth Service on port $PORT..."
echo "📊 Debug mode: $DEBUG"
echo "🔑 Using SECRET_KEY: ${SECRET_KEY:0:10}..."
echo "🗄️  Database: ${DATABASE_URL%%@*}@***"
echo "⏰ Token expiry: $ACCESS_TOKEN_EXPIRE_MINUTES minutes"

# Use uv from PATH (works in both Docker and local environments)
UV_CMD="uv"
if [ -f "/opt/homebrew/bin/uv" ]; then
    UV_CMD="/opt/homebrew/bin/uv"
fi

# Run the auth service
$UV_CMD run uvicorn src.auth_service.main:app --reload --host $HOST --port $PORT
