# 🤖 RAG (Retrieval-Augmented Generation) Service

A **production-ready RAG application** that combines vector search with AI-powered responses for intelligent document management and question answering.

## 🎯 **What is RAG?**

**RAG (Retrieval-Augmented Generation)** is a revolutionary AI technique that:

1. **🔍 Retrieves** relevant information from your knowledge base
2. **🤖 Generates** intelligent, contextual responses using AI
3. **✅ Provides** factual, up-to-date information with source attribution

### **Why RAG is Game-Changing**

Traditional AI has limitations:
- ❌ **Knowledge cutoff**: Only knows what it was trained on
- ❌ **Hallucinations**: Can make up false information  
- ❌ **No sources**: Can't verify where information comes from

RAG solves these by:
- ✅ **Always current**: Uses your latest documents and data
- ✅ **Factual responses**: Grounded in real information
- ✅ **Source transparency**: Shows exactly which documents were used
- ✅ **Customizable**: Tailored to your specific domain

## 🚀 **Quick Start**

### **Get Running in 5 Minutes**

1. **Start all services**:
   ```bash
   ./run_all.sh
   ```

2. **Set your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Upload a document**:
   ```bash
   curl -X POST "http://localhost:8003/api/v1/documents/upload" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "file=@your_document.pdf" \
     -F "title=Medical Guidelines" \
     -F "document_type=guidelines"
   ```

4. **Ask a question**:
   ```bash
   curl -X POST "http://localhost:8003/api/v1/chat/ask" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "What are the treatment guidelines?"}'
   ```

**📖 For detailed instructions, see [QUICK_START.md](QUICK_START.md)**

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Vector Search  │───▶│  AI Generation  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Document Store │    │  Context-Aware  │
                       │  (pgvector)     │    │   Response      │
                       └─────────────────┘    └─────────────────┘
```

### **Core Components**

- **📚 Document Processing**: Upload, chunk, and embed documents
- **🔍 Vector Search**: Semantic similarity search with pgvector
- **🤖 AI Generation**: OpenAI GPT-powered responses
- **🔐 Authorization**: Role-based access control with Oso
- **🌐 Web Interface**: React-based frontend for easy interaction

## ✨ **Key Features**

### **🔍 Intelligent Document Search**
- **Semantic search**: Find documents even without exact keywords
- **Department filtering**: Search within specific departments
- **Document type filtering**: Filter by guidelines, research, procedures
- **Similarity scoring**: Configurable relevance thresholds

### **🤖 AI-Powered Q&A**
- **Context-aware responses**: Uses relevant documents to inform answers
- **Role-based responses**: Tailored for doctors, nurses, administrators
- **Source attribution**: Shows which documents were used
- **Fallback handling**: Graceful responses when no context is found

### **🔐 Enterprise Security**
- **JWT authentication**: Secure user sessions
- **Oso authorization**: Fine-grained access control
- **Department isolation**: Users only see their department's documents
- **Audit trails**: Track all document access and modifications

### **📊 Monitoring & Analytics**
- **Embedding status tracking**: Monitor document processing
- **Performance metrics**: Track response times and quality
- **Health checks**: Service monitoring and diagnostics

## 🎯 **Use Cases**

### **🏥 Healthcare**
- **Medical Guidelines**: Quick access to latest treatment protocols
- **Patient Documentation**: Search through patient records and notes
- **Research Papers**: Find relevant medical research and studies
- **Procedure Manuals**: Access step-by-step clinical procedures

### **💼 Business**
- **Policy Documents**: Search company policies and procedures
- **Training Materials**: Access onboarding and training content
- **Technical Documentation**: Find product and system documentation
- **Knowledge Base**: Centralized organizational knowledge

### **🎓 Education**
- **Course Materials**: Search through educational content
- **Research Papers**: Access academic literature and studies
- **Study Guides**: Find relevant study materials and resources

## 📚 **Documentation**

- **🚀 [Quick Start Guide](QUICK_START.md)**: Get up and running in 5 minutes
- **📖 [Complete User Guide](RAG_GUIDE.md)**: Comprehensive usage instructions
- **🚀 [Enhancement Ideas](ENHANCEMENTS.md)**: Advanced features and improvements
- **🔧 [API Documentation](http://localhost:8003/docs)**: Interactive API docs

## 🛠️ **Technology Stack**

- **🐍 Backend**: FastAPI with SQLAlchemy
- **🗄️ Database**: PostgreSQL with pgvector extension
- **🧠 AI**: OpenAI GPT and embedding models
- **🔐 Security**: Oso authorization, JWT authentication
- **🌐 Frontend**: React with TypeScript
- **📦 Package Management**: uv workspaces

## 🔧 **Configuration**

### **Environment Variables**
```env
# Core Configuration
DEBUG=true
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CONTEXT_LENGTH=8000
SIMILARITY_THRESHOLD=0.7
MAX_RESULTS=5
```

## 🚀 **Getting Started**

### **Prerequisites**
- Python 3.11+
- PostgreSQL with pgvector extension
- OpenAI API key
- uv package manager

### **Installation**
```bash
# From project root
uv sync

# Or from package directory
cd packages/rag
uv sync
```

### **Running the Service**
```bash
# Set environment variables
export PYTHONPATH="../common/src:$PYTHONPATH"
export OPENAI_API_KEY="your-openai-api-key-here"

# Start the service
uv run uvicorn src.rag_service.main:app --reload --port 8003

# Or use the run script
./run.sh
```

## Performance Considerations

### Embedding Generation
- Batch processing for multiple documents
- Async operations to prevent blocking
- Error handling for API rate limits

### Vector Search
- Database-level similarity calculations
- Indexed vector columns for fast retrieval
- Result limiting to prevent large responses

### Token Management
- Context length monitoring
- Smart truncation for long contexts
- Token counting for cost estimation

## Security Features

- **API Key Security:** OpenAI keys stored in environment variables
- **Content Filtering:** Sensitive document access controls
- **Audit Trail:** Document creation and access logging
- **Input Validation:** Sanitization of user inputs
- **Rate Limiting:** Protection against API abuse

## Cost Optimization

### OpenAI Usage
- Use smaller embedding models when possible
- Implement caching for frequently accessed embeddings
- Monitor token usage for cost tracking
- Use cheaper chat models for non-critical responses

### Database Optimization
- Efficient vector storage with pgvector
- Proper indexing strategies
- Query optimization for large document sets

## Troubleshooting

### Common Issues

1. **OpenAI API errors:** Check API key and quota limits
2. **Vector search issues:** Ensure pgvector extension is installed
3. **Import errors:** Verify PYTHONPATH includes `../common/src`
4. **Embedding failures:** Check network connectivity and API limits
5. **Performance issues:** Monitor database query performance

### Debug Mode

Set `DEBUG=true` for detailed logging:
- Embedding generation logs
- Vector search query details
- AI response generation steps
- Authorization decision logging

### Monitoring

Key metrics to monitor:
- OpenAI API usage and costs
- Vector search performance
- Document processing success rates
- User query patterns
- Response quality feedback

## Integration

This service integrates with:
- **Auth Service:** User authentication and role information
- **Patient Service:** Patient-specific document context
- **Common Package:** Shared models and database utilities
- **OpenAI API:** Embeddings and chat completions
- **PostgreSQL + pgvector:** Vector storage and similarity search

## Contributing

1. Follow existing async/await patterns for AI operations
2. Add comprehensive error handling for external API calls
3. Update vector search logic carefully to maintain performance
4. Test with various document types and sizes
5. Consider cost implications of AI model changes
6. Update this README for new features and configuration options

## Future Enhancements

- Conversation history storage
- Advanced search filters
- Document summarization
- Multi-language support
- Custom embedding models
- Response quality analytics
