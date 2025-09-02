# 📊 Galileo Observability Integration

This document explains the **standard Galileo observability integration** for the RAG service, which uses only Galileo for comprehensive monitoring and analytics.

## 🎯 Overview

The observability system uses:
- **Galileo SDK** for event logging and monitoring
- **Structured logging** with structlog

## 🔧 Configuration

### Environment Variables

```env
# Galileo Observability
GALILEO_ENABLED=true
GALILEO_API_KEY=your-galileo-api-key-here
GALILEO_PROJECT_NAME=healthcare-rag
GALILEO_ENVIRONMENT=development

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Galileo Setup

1. **Get your Galileo API key** from the Galileo platform
2. **Set the project name** to match your Galileo project
3. **Configure environment** (development/staging/production)
4. **Enable observability** by setting `GALILEO_ENABLED=true`

## 📊 What Gets Tracked

### RAG Operations
- **Query processing** (start, completion, errors)
- **Embedding generation** (model, chunk count, duration)
- **Vector search** (results, similarity threshold, duration)
- **AI response generation** (model, token count, duration)

### Document Operations
- **Document uploads** (type, department, file size)
- **Embedding storage** (document ID, chunk count)

### HTTP Requests
- **Request completion** (method, path, duration, status)
- **Request failures** (error details)

### Event Tracking
- **All operations logged to Galileo** with rich metadata
- **User context tracking** when available
- **Session tracking** for request correlation

## 🚀 Usage Examples

### Basic Event Logging

```python
from .observability import log_galileo_event

# Log a custom event
log_galileo_event(
    event_type="custom_operation",
    event_data={
        "operation": "data_processing",
        "records_processed": 1000,
        "duration": 5.2
    },
    user_id="user123",
    session_id="session456"
)
```

### Context Managers for Operations

```python
from .observability import rag_query_context

async with rag_query_context(
    query_type="document_search",
    user_role="doctor",
    department="cardiology"
) as query_id:
    # Your RAG operation here
    results = await search_documents(query)
    return results
```

### Document Upload Tracking

```python
from .observability import log_document_upload

log_document_upload(
    document_type="guidelines",
    department="cardiology",
    file_size=1024000,
    document_id=123
)
```

## 📈 Monitoring Dashboard

### Galileo Events

All events are automatically logged to Galileo with:
- **Event type** (e.g., `rag_query_completed`)
- **Event data** (operation details, metrics, timestamps)
- **User context** (when available)
- **Session tracking** (when available)

### Event Types

The system logs these event types to Galileo:

```
# RAG Operations
rag_query_started
rag_query_completed
rag_query_failed

# Embedding Operations
embedding_generation_started
embedding_generation_completed
embedding_generation_failed

# Vector Search Operations
vector_search_started
vector_search_completed
vector_search_failed

# AI Response Operations
ai_response_generation_started
ai_response_generation_completed
ai_response_generation_failed

# Document Operations
document_uploaded
embeddings_stored

# HTTP Operations
http_request_completed
http_request_failed
```

## 🔍 Observability Endpoints

### Health Check
```bash
curl http://localhost:8003/health
```

### Observability Status
```bash
curl http://localhost:8003/observability
```

## 🛠️ Development

### Adding New Events

1. **Define event type** in your operation
2. **Use context managers** for automatic tracking
3. **Log custom events** with `log_galileo_event()`

### Testing Observability

```python
# Test Galileo connection
curl -X GET "http://localhost:8003/observability"

# Check if events are being logged
# Monitor Galileo dashboard for new events
```

## 🚀 Production Deployment

### Galileo Configuration

```env
# Production Galileo settings
GALILEO_ENABLED=true
GALILEO_API_KEY=your-production-galileo-api-key
GALILEO_PROJECT_NAME=healthcare-rag-prod
GALILEO_ENVIRONMENT=production
```

### Monitoring Setup

1. **Configure Galileo alerts** for error rates
2. **Create dashboards** for key metrics
3. **Configure log aggregation** for structured logs
4. **Set up event-based monitoring** for critical operations

## 🔧 Troubleshooting

### Galileo Connection Issues

```bash
# Check Galileo configuration
curl -X GET "http://localhost:8003/observability"

# Verify API key is set
echo $GALILEO_API_KEY

# Check Galileo SDK logs
tail -f logs/rag.log | grep -i galileo
```

### Logging Issues

```bash
# Check log format
grep "LOG_FORMAT" packages/rag/.env

# View structured logs
tail -f logs/rag.log | jq .
```

## 📚 Key Benefits

### Simplified Architecture
- **No OTEL complexity** - direct Galileo integration
- **No Prometheus setup** - Galileo handles all metrics
- **Reduced dependencies** - fewer packages to manage
- **Easier deployment** - single observability platform

### Rich Observability
- **Comprehensive event tracking** - all RAG operations
- **Structured logging** - machine-readable logs
- **User context** - track user behavior
- **Session correlation** - link related operations

### Production Ready
- **Error tracking** - automatic error logging
- **Performance monitoring** - duration tracking
- **Scalable** - handles high-volume operations
- **Secure** - API key-based authentication

## 🎯 Next Steps

1. **Configure Galileo API key** in your environment
2. **Set up monitoring dashboards** in Galileo
3. **Configure alerts** for error conditions
4. **Monitor performance** and optimize based on events
5. **Set up custom event tracking** for business metrics

---

**Note**: This observability system provides comprehensive monitoring using only Galileo, making it easier to deploy and maintain while still providing rich insights into your RAG system's performance and usage.
