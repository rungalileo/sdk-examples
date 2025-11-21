# RAG Service

AI-powered document search and question answering service for the Healthcare Support Portal.

## Features

- Document embedding generation using OpenAI
- Vector similarity search with pgvector
- Context-aware AI responses
- Role-based access control with Oso
- Galileo observability integration

## API Endpoints

- `POST /api/v1/chat/ask` - Ask AI questions with RAG context
- `POST /api/v1/chat/search` - Search documents by similarity
- `POST /api/v1/documents/upload` - Upload and process documents
- `GET /api/v1/documents/` - List authorized documents

## Configuration

Configure the service using environment variables in `.env`:

- `OPENAI_API_KEY` - Required for embeddings and chat
- `GALILEO_API_KEY` - Optional for observability  
- `DATABASE_URL` - PostgreSQL connection string
- `OSO_URL` - Oso authorization server URL

## Running

```bash
uv run uvicorn src.rag_service.main:app --reload --host 0.0.0.0 --port 8003
```

Or use the provided script:

```bash
./run.sh
```
