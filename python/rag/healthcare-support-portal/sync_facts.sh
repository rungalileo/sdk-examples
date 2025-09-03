#!/bin/bash

# Healthcare Support Portal - OSO Facts Synchronization
# Convenience script to sync authorization facts with OSO Cloud

# Exit on any error
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🔐 Healthcare Support Portal - OSO Fact Synchronization"
echo "======================================================"

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

# Check if we're in the right directory
if [ ! -f "packages/common/src/common/sync_oso_facts.py" ] && [ ! -f "sync_oso_facts.py" ]; then
    echo "❌ Cannot find sync_oso_facts.py script."
    echo "   Please run this from the project root directory."
    exit 1
fi

echo "🚀 Running fact synchronization..."

# Run the fact synchronization script
if ! $UV_CMD run python -m packages.common.src.common.sync_oso_facts; then
    echo "❌ Failed to synchronize OSO facts"
    exit 1
fi

echo "✅ OSO facts synchronized successfully!"
