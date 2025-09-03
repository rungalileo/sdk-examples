#!/bin/bash
# run.sh - Start Healthcare Support Portal Frontend Service

# Exit on any error
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🌐 Starting Healthcare Support Portal Frontend Service..."

# Check for Node.js and npm
if ! command_exists node; then
    echo "❌ Node.js not found. Please install Node.js 20.19.0+ and try again."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm not found. Please install npm and try again."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | sed 's/v//')
if [ "$(printf '%s\n' "20.19.0" "$NODE_VERSION" | sort -V | head -n1)" != "20.19.0" ]; then
    echo "❌ Node.js $NODE_VERSION found, but 20.19.0+ is required."
    exit 1
fi
echo "✅ Node.js $NODE_VERSION is compatible"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    if ! npm install; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
else
    echo "✅ Dependencies found"
fi

# Check if port 3000 is available
if command_exists lsof; then
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Port 3000 is already in use"
        echo "Please stop the service using port 3000 or change the port in vite.config.ts"
        exit 1
    fi
else
    echo "⚠️  Warning: lsof not found. Cannot check if port 3000 is available."
fi

echo "🚀 Starting development server on http://localhost:3000"
if ! npm run dev; then
    echo "❌ Failed to start frontend development server"
    exit 1
fi
