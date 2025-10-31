#!/bin/bash
# stop_all.sh - Stop all Healthcare Support Portal services

# Don't exit on error for this script (we want to try stopping all services)
# set -e would cause the script to exit if one service isn't running

echo "🛑 Healthcare Support Portal - Stopping All Services"
echo "=================================================="

# Function to stop a service by PID file
stop_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Stopping $service_name (PID: $pid)..."
            kill "$pid"
            rm "$pid_file"
        else
            echo "⚠️  $service_name was not running (stale PID file)"
            rm "$pid_file"
        fi
    else
        echo "⚠️  No PID file found for $service_name"
    fi
}

# Stop all services
stop_service "auth"
stop_service "patient"
stop_service "rag"
stop_service "frontend"

# Also try to kill any remaining uvicorn processes for our services
echo "🧹 Cleaning up any remaining processes..."
if command -v pkill >/dev/null 2>&1; then
    pkill -f "src.auth_service.main:app" 2>/dev/null || true
    pkill -f "src.patient_service.main:app" 2>/dev/null || true
    pkill -f "src.rag_service.main:app" 2>/dev/null || true
    # Also kill any npm/node processes for frontend
    pkill -f "react-router dev" 2>/dev/null || true
else
    echo "⚠️  pkill not available. Manual cleanup may be needed."
fi

echo ""
echo "✅ All services stopped!"
echo "🗄️  Database is still running. Use 'docker-compose down' to stop it."
echo "   To stop everything including database: docker-compose down"
