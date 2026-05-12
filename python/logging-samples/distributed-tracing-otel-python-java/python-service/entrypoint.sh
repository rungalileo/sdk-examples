#!/bin/sh
set -e

echo "Seeding ChromaDB..."
python seed_chroma.py

echo "Starting RAG service..."
exec uvicorn app:app --host 0.0.0.0 --port 8099
