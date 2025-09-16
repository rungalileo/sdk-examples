#!/bin/bash
#
# Healthcare Support Portal - Environment Validation Script
# This script checks that all required dependencies and ports are available
#

echo "🔍 Validating environment..."
echo "=============================="

# Check required software
echo "📋 Checking required software:"

python3 --version >/dev/null 2>&1 && echo "✅ Python OK" || echo "❌ Install Python 3.11+"
node --version >/dev/null 2>&1 && echo "✅ Node.js OK" || echo "❌ Install Node.js 20.19.0+"
docker --version >/dev/null 2>&1 && echo "✅ Docker OK" || echo "❌ Install Docker"
git --version >/dev/null 2>&1 && echo "✅ Git OK" || echo "❌ Install Git"
command -v uv >/dev/null 2>&1 && echo "✅ UV package manager OK" || echo "❌ Install UV package manager"

echo
echo "🔌 Checking port availability:"

# Check available ports
for port in 3000 8001 8002 8003 5432 8080; do
  if ! lsof -i :$port > /dev/null 2>&1; then
    echo "✅ Port $port available"
  else
    echo "⚠️ Port $port in use - you may need to stop other services"
  fi
done

echo
echo "🎉 Environment validation complete!"
echo "If any checks failed, see the troubleshooting section in README.md"
