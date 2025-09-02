#!/bin/bash

# Healthcare Support Portal - OSO Facts Synchronization
# Convenience script to sync authorization facts with OSO Cloud

echo "🔐 Healthcare Support Portal - OSO Fact Synchronization"
echo "======================================================"

# Use uv from PATH (works in both Docker and local environments)
UV_CMD="uv"
if [ -f "/opt/homebrew/bin/uv" ]; then
    UV_CMD="/opt/homebrew/bin/uv"
fi

# Run the fact synchronization script
$UV_CMD run python -m packages.common.src.common.sync_oso_facts
