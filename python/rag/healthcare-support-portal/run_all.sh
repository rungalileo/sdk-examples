#!/bin/bash
# run_all.sh - Start all Healthcare Support Portal services and infrastructure

echo "🏥 Healthcare Support Portal - Starting All Services"
echo "=================================================="

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Check if required ports are available
echo "🔍 Checking port availability..."
check_port 8001 || exit 1
check_port 8002 || exit 1
check_port 8003 || exit 1
check_port 3000 || exit 1

# Special handling for port 8080 (Oso Dev Server) - informational only
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "ℹ️  Port 8080 is in use (Oso Dev Server likely running)"
else
    echo "✅ Port 8080 is available"
fi

echo ""
echo "🚀 Starting services..."

# Start infrastructure services if not running
echo "🏗️  Checking infrastructure services..."
if ! docker ps | grep -q healthcare-support-portal; then
    echo "Starting PostgreSQL database and Oso Dev Server..."
    docker-compose up -d db oso
    echo "Waiting for database to be ready..."
    sleep 8
    echo "Running database migrations..."
    docker-compose run --rm migrate
    echo "✅ Database migrations completed"
else
    echo "✅ Infrastructure services (PostgreSQL + Oso Dev Server) are already running"
    echo "🔍 Checking if migrations are current..."
    docker-compose run --rm migrate
fi

# Create logs directory if it doesn't exist
echo "📁 Creating logs directory..."
if ! mkdir -p logs 2>/dev/null; then
    echo "⚠️  Warning: Could not create logs directory. Output will go to console."
    LOG_TO_FILE=false
else
    LOG_TO_FILE=true
fi

# Get absolute path for logs
ROOT_DIR=$(pwd)

# Start services in background using subshells to avoid directory changes
echo "🔐 Starting Auth Service..."
if [ "$LOG_TO_FILE" = true ]; then
    (cd packages/auth && ./run.sh) > "$ROOT_DIR/logs/auth.log" 2>&1 &
else
    (cd packages/auth && ./run.sh) &
fi
AUTH_PID=$!

echo "🏥 Starting Patient Service..."
if [ "$LOG_TO_FILE" = true ]; then
    (cd packages/patient && ./run.sh) > "$ROOT_DIR/logs/patient.log" 2>&1 &
else
    (cd packages/patient && ./run.sh) &
fi
PATIENT_PID=$!

echo "🤖 Starting RAG Service..."
if [ "$LOG_TO_FILE" = true ]; then
    (cd packages/rag && ./run.sh) > "$ROOT_DIR/logs/rag.log" 2>&1 &
else
    (cd packages/rag && ./run.sh) &
fi
RAG_PID=$!

echo "🌐 Starting Frontend Service..."
if [ "$LOG_TO_FILE" = true ]; then
    (cd frontend && ./run.sh) > "$ROOT_DIR/logs/frontend.log" 2>&1 &
else
    (cd frontend && ./run.sh) &
fi
FRONTEND_PID=$!

echo ""
echo "✅ All services started!"
echo "=================================================="
echo "🌐 Frontend:        http://localhost:3000"
echo "🔐 Auth Service:    http://localhost:8001/docs"
echo "🏥 Patient Service: http://localhost:8002/docs"
echo "🤖 RAG Service:     http://localhost:8003/docs"
echo "⚖️  Oso Dev Server:  http://localhost:8080"
echo ""
echo "📋 Service PIDs:"
echo "   Frontend Service: $FRONTEND_PID"
echo "   Auth Service: $AUTH_PID"
echo "   Patient Service: $PATIENT_PID"
echo "   RAG Service: $RAG_PID"
if [ "$LOG_TO_FILE" = true ]; then
    echo "📄 Logs are available in the logs/ directory"
else
    echo "📄 Service output is displayed in console"
fi
echo "🛑 To stop all services, run: ./stop_all.sh"
echo ""

# Save PIDs for stopping later (create logs directory if needed for PID files)
if [ "$LOG_TO_FILE" = true ] || mkdir -p logs 2>/dev/null; then
    echo "$FRONTEND_PID" > logs/frontend.pid
    echo "$AUTH_PID" > logs/auth.pid
    echo "$PATIENT_PID" > logs/patient.pid
    echo "$RAG_PID" > logs/rag.pid
else
    echo "⚠️  Warning: Could not save PID files. You'll need to stop services manually."
fi

# Wait for user input
echo "Press Ctrl+C to stop all services..."
trap 'echo ""; echo "🛑 Stopping all services..."; kill $FRONTEND_PID $AUTH_PID $PATIENT_PID $RAG_PID 2>/dev/null; exit 0' INT

# Keep script running
wait
