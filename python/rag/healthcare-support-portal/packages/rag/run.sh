#!/bin/bash
# packages/rag/run.sh

# Exit on any error
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Load .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    set -o allexport
    source .env
    set +o allexport
else
    echo "⚠️  Warning: No .env file found. Using defaults."
fi

# Set PYTHONPATH to include common package
export PYTHONPATH="../common/src:$PYTHONPATH"

# Set default environment variables if not already set
export SECRET_KEY="${SECRET_KEY:-your-secret-key-here}"
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare}"
export DEBUG="${DEBUG:-true}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8003}"

# OpenAI Configuration
export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
export EMBEDDING_MODEL="${EMBEDDING_MODEL:-text-embedding-3-small}"
export CHAT_MODEL="${CHAT_MODEL:-gpt-4o-mini}"

# RAG Configuration
export CHUNK_SIZE="${CHUNK_SIZE:-1000}"
export CHUNK_OVERLAP="${CHUNK_OVERLAP:-200}"
export MAX_CONTEXT_LENGTH="${MAX_CONTEXT_LENGTH:-8000}"
export SIMILARITY_THRESHOLD="${SIMILARITY_THRESHOLD:-0.7}"
export MAX_RESULTS="${MAX_RESULTS:-5}"

echo "🤖 Starting RAG Service on port $PORT..."
echo "📊 Debug mode: $DEBUG"
echo "🔑 Using SECRET_KEY: ${SECRET_KEY:0:10}..."
echo "🗄️  Database: ${DATABASE_URL%%@*}@***"
echo "🧠 OpenAI API Key: ${OPENAI_API_KEY:0:10}${OPENAI_API_KEY:10:1}..."
echo "📝 Embedding Model: $EMBEDDING_MODEL"
echo "💬 Chat Model: $CHAT_MODEL"
echo "🔍 Similarity Threshold: $SIMILARITY_THRESHOLD"

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY is not set. RAG functionality will not work."
    echo "   Please set your OpenAI API key in the .env file or environment variables."
fi

# Check for uv command
UV_CMD="uv"
if [ -f "/opt/homebrew/bin/uv" ]; then
    UV_CMD="/opt/homebrew/bin/uv"
fi

if ! command_exists "$UV_CMD"; then
    echo "❌ uv package manager not found. Please install uv and try again."
    echo "   Installation: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if port is available
if command_exists lsof; then
    if lsof -i :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Port $PORT is already in use. Please stop the service using this port."
        exit 1
    fi
fi

# Check essential environment variables
if [ "$SECRET_KEY" = "your-secret-key-here" ] || [ "$SECRET_KEY" = "change-me-in-production" ]; then
    echo "⚠️  WARNING: Using default SECRET_KEY. This is insecure for production!"
fi

# Run the RAG service
echo "🚀 Starting uvicorn server..."
if ! $UV_CMD run uvicorn src.rag_service.main:app --reload --host $HOST --port $PORT; then
    echo "❌ Failed to start RAG Service"
    exit 1
fi
