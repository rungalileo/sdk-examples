#!/usr/bin/env bash
set -euo pipefail

# Run the notebooks-integration GitHub Actions workflow locally using act (Docker)

WORKFLOW_FILE=".github/workflows/notebooks-integration.yaml"

if ! command -v act >/dev/null 2>&1; then
  echo "ERROR: 'act' is not installed." >&2
  echo "Install it e.g. with Homebrew: brew install act" >&2
  exit 1
fi

SECRETS_FILE="${SECRETS_FILE:-.secrets}"
if [ ! -f "$SECRETS_FILE" ]; then
  echo "ERROR: Secrets file '$SECRETS_FILE' not found." >&2
  echo "Copy '.secrets.example' to '.secrets' and fill in the values." >&2
  exit 1
fi

if [ ! -f "$WORKFLOW_FILE" ]; then
  echo "ERROR: Workflow file '$WORKFLOW_FILE' not found. Run from repo root." >&2
  exit 1
fi

# Determine container architecture for Apple Silicon vs Intel
ARCH="$(uname -m)"
if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
  CONTAINER_ARCH="linux/arm64"
else
  CONTAINER_ARCH="linux/amd64"
fi

# Default GitHub Actions runner image mapping for ubuntu-latest
# You can override by setting ACT_IMAGE env var
IMAGE="${ACT_IMAGE:-catthehacker/ubuntu:act-latest}"

# Event to simulate (workflow_dispatch by default). Alternatives: push, pull_request
EVENT="${1:-workflow_dispatch}"

set -x
act "$EVENT" \
  -W "$WORKFLOW_FILE" \
  --secret-file "$SECRETS_FILE" \
  -P ubuntu-latest="$IMAGE" \
  --container-architecture "$CONTAINER_ARCH" \
  --rm


