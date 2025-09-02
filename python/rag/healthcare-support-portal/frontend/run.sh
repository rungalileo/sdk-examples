#!/bin/bash
# run.sh - Start Healthcare Support Portal Frontend Service

echo "🌐 Starting Healthcare Support Portal Frontend Service..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if port 3000 is available
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ Port 3000 is already in use"
    echo "Please stop the service using port 3000 or change the port in vite.config.ts"
    exit 1
fi

echo "🚀 Starting development server on http://localhost:3000"
npm run dev