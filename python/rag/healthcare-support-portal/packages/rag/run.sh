#!/bin/bash
# packages/rag/run.sh

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

# Use uv from PATH (works in both Docker and local environments)
UV_CMD="uv"
if [ -f "/opt/homebrew/bin/uv" ]; then
    UV_CMD="/opt/homebrew/bin/uv"
fi

# Run the RAG service
$UV_CMD run uvicorn src.rag_service.main:app --reload --host $HOST --port $PORT
