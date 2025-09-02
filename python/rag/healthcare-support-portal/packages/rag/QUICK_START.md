# 🚀 RAG Application Quick Start Guide

## ⚡ **Get Your RAG System Running in 5 Minutes**

Your RAG application is already built and ready to use! Here's how to get started:

## 📋 **Prerequisites**

Make sure you have:
- ✅ Python 3.11+
- ✅ PostgreSQL with pgvector extension
- ✅ OpenAI API key
- ✅ uv package manager

## 🚀 **Step 1: Start All Services**

From the project root, run:

```bash
# Start all services (auth, patient, rag, frontend, database)
./run_all.sh
```

This will start:
- 🔐 **Auth Service** (Port 8001)
- 🏥 **Patient Service** (Port 8002) 
- 🤖 **RAG Service** (Port 8003)
- 🌐 **Frontend** (Port 3000)
- 🗄️ **PostgreSQL** (Port 5432)

## 🔑 **Step 2: Get Your API Key**

1. **Sign up for OpenAI**: https://platform.openai.com/
2. **Create an API key**: Go to API Keys section
3. **Set the environment variable**:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## 👤 **Step 3: Create a Test User**

Your system comes with seed data, but you can create a test user:

```bash
# Login to the frontend at http://localhost:3000
# Or use the API directly:

curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "password123",
    "role": "doctor",
    "department": "cardiology"
  }'
```

## 📚 **Step 4: Upload Your First Document**

```bash
# Get a JWT token first
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "password123"
  }'

# Use the token to upload a document
curl -X POST "http://localhost:8003/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@your_document.pdf" \
  -F "title=Medical Guidelines" \
  -F "document_type=guidelines" \
  -F "department=cardiology"
```

## 🤖 **Step 5: Ask Your First Question**

```bash
curl -X POST "http://localhost:8003/api/v1/chat/ask" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the treatment guidelines for heart disease?",
    "context_department": "cardiology"
  }'
```

## 🎯 **Step 6: Explore the Web Interface**

Open your browser and go to: **http://localhost:3000**

You'll see:
- 📚 **Document Management**: Upload and manage documents
- 🔍 **Search Interface**: Search through your documents
- 💬 **Chat Interface**: Ask questions and get AI-powered responses
- 👥 **User Management**: Manage users and permissions

## 📊 **Step 7: Monitor Your System**

### **Check Service Health**
```bash
# RAG Service
curl http://localhost:8003/health

# Auth Service  
curl http://localhost:8001/health

# Patient Service
curl http://localhost:8002/health
```

### **Check Embedding Status**
```bash
curl -X GET "http://localhost:8003/api/v1/documents/embedding-statuses" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🧪 **Step 8: Test Different Scenarios**

### **Test Document Search**
```bash
curl -X POST "http://localhost:8003/api/v1/chat/search" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "diabetes treatment",
    "document_types": ["guidelines", "research"],
    "limit": 5
  }'
```

### **Test Role-Based Responses**
Try asking the same question as different user roles:
- **Doctor**: "What are the contraindications for metformin?"
- **Nurse**: "How do I administer insulin safely?"
- **Admin**: "What are the HIPAA compliance requirements?"

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Service Won't Start**
```bash
# Check if ports are available
lsof -i :8001
lsof -i :8002  
lsof -i :8003
lsof -i :3000
```

#### **Database Connection Issues**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs healthcare-support-portal-postgres-1
```

#### **OpenAI API Errors**
```bash
# Verify your API key
echo $OPENAI_API_KEY

# Test OpenAI connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

#### **No Documents Found**
```bash
# Check if documents are properly embedded
curl -X GET "http://localhost:8003/api/v1/documents/embedding-statuses" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Regenerate embeddings if needed
curl -X POST "http://localhost:8003/api/v1/documents/{doc_id}/regenerate-embeddings" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📈 **Next Steps**

Once you're up and running:

1. **📚 Upload More Documents**: Add your organization's knowledge base
2. **👥 Create More Users**: Set up different roles and departments
3. **🔍 Test Search Quality**: Try various queries and refine results
4. **📊 Monitor Performance**: Track response times and user satisfaction
5. **🚀 Explore Advanced Features**: Check out the enhancement guide

## 🎯 **Success Metrics**

You'll know your RAG system is working well when:

- ✅ **Fast Response Times**: Queries return results in under 2 seconds
- ✅ **Relevant Results**: Search results match your queries well
- ✅ **Accurate Responses**: AI responses are grounded in your documents
- ✅ **User Satisfaction**: Users find the system helpful and accurate

## 📚 **Additional Resources**

- **📖 Complete User Guide**: `RAG_GUIDE.md`
- **🚀 Enhancement Ideas**: `ENHANCEMENTS.md`
- **🔧 API Documentation**: http://localhost:8003/docs
- **🌐 Web Interface**: http://localhost:3000

---

**🎉 Congratulations! You now have a fully functional RAG system that can transform how your organization accesses and uses knowledge!**

**Need help?** Check the troubleshooting section or explore the complete user guide for detailed information.
