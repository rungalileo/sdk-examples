# 🧠 RAG Application: 

## 🎯 **What is RAG and Why It Matters**

**RAG (Retrieval-Augmented Generation)** is a powerful AI technique that combines the best of both worlds:

1. **🔍 Retrieval**: Find relevant information from your knowledge base
2. **🤖 Generation**: Use AI to create intelligent, contextual responses

### **Why RAG is Revolutionary**

Traditional AI models have limitations:
- ❌ **Knowledge cutoff**: They only know what they were trained on
- ❌ **Hallucinations**: They can make up false information
- ❌ **No source attribution**: You can't verify where information comes from

RAG solves these problems by:
- ✅ **Always up-to-date**: Uses your current documents and data
- ✅ **Factual responses**: Grounded in real information from your knowledge base
- ✅ **Source transparency**: Shows you exactly which documents were used
- ✅ **Customizable**: Tailored to your specific domain and use case

## 🏗️ **Your RAG System Architecture**

Your RAG application follows a sophisticated, production-ready architecture:

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

### **🔍 Step 1: Document Processing**
```
Upload Document → Text Extraction → Chunking → Embedding Generation → Vector Storage
```

### **🔍 Step 2: Query Processing**
```
User Question → Query Embedding → Similarity Search → Context Retrieval
```

### **🤖 Step 3: Response Generation**
```
Retrieved Context + User Role + Question → OpenAI GPT → Contextual Response
```

## 🚀 **How to Use Your RAG System**

### **1. 📚 Document Management**

#### **Uploading Documents**
```bash
# Upload a document via API
curl -X POST "http://localhost:8003/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@medical_guidelines.pdf" \
  -F "title=Medical Guidelines 2024" \
  -F "document_type=guidelines" \
  -F "department=cardiology"
```

#### **Document Types Supported**
- **PDF files**: Medical reports, guidelines, research papers
- **Text files**: Notes, procedures, policies
- **Word documents**: Clinical documentation

#### **Automatic Processing**
When you upload a document, the system automatically:
1. **Extracts text** from the document
2. **Chunks the content** into manageable pieces (1000 tokens with 200 token overlap)
3. **Generates embeddings** using OpenAI's `text-embedding-3-small`
4. **Stores vectors** in PostgreSQL with pgvector
5. **Applies authorization** rules based on user roles

### **2. 🔍 Searching Documents**

#### **Vector Similarity Search**
```bash
# Search for relevant documents
curl -X POST "http://localhost:8003/api/v1/chat/search" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "heart attack symptoms",
    "document_types": ["guidelines", "research"],
    "department": "cardiology",
    "limit": 10
  }'
```

#### **Search Features**
- **Semantic search**: Finds documents even if they don't contain exact keywords
- **Department filtering**: Search within specific departments
- **Document type filtering**: Filter by guidelines, research, procedures, etc.
- **Similarity threshold**: Configurable relevance scoring

### **3. 🤖 AI-Powered Q&A**

#### **Asking Questions**
```bash
# Ask a question and get AI-powered response
curl -X POST "http://localhost:8003/api/v1/chat/ask" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the latest treatment guidelines for diabetes?",
    "context_patient_id": 123,
    "context_department": "endocrinology",
    "max_results": 5
  }'
```

#### **Response Features**
- **Context-aware**: Uses relevant documents to inform responses
- **Role-based**: Tailored responses for doctors, nurses, and administrators
- **Source attribution**: Shows which documents were used
- **Fallback handling**: Graceful responses when no relevant context is found

## 🎯 **Role-Based RAG Experience**

### **👨‍⚕️ Doctor Experience**
```python
# Doctors get professional medical responses
system_prompt = """You are an AI assistant helping a doctor in a healthcare setting. 
Provide accurate, professional medical information based on the provided context. 
Always remind users to verify information and consult current medical guidelines."""
```

**Example Doctor Query**: "What are the contraindications for prescribing metformin?"
**RAG Response**: Uses latest medical guidelines and research papers to provide evidence-based information.

### **👩‍⚕️ Nurse Experience**
```python
# Nurses get practical care information
system_prompt = """You are an AI assistant helping a nurse in a healthcare setting. 
Provide practical, relevant information for nursing care based on the provided context. 
Focus on procedures, patient care, and safety protocols."""
```

**Example Nurse Query**: "How do I properly administer insulin to a patient?"
**RAG Response**: Uses nursing procedures and safety guidelines for step-by-step instructions.

### **👨‍💼 Administrator Experience**
```python
# Administrators get policy and procedure information
system_prompt = """You are an AI assistant helping a healthcare administrator. 
Provide information about policies, procedures, and administrative matters based on the provided context."""
```

**Example Admin Query**: "What are the HIPAA compliance requirements for patient data?"
**RAG Response**: Uses policy documents and compliance guidelines.

## 🔐 **Security & Authorization**

### **Oso Authorization System**
Your RAG system uses Oso for fine-grained access control:

```python
# Example authorization rules
allow(user: User, "read", document: Document) if
    user.role == "admin" or
    user.department == document.department or
    document.patient_id in user.assigned_patients;
```

### **Access Control Features**
- **Role-based access**: Different permissions for doctors, nurses, admins
- **Department isolation**: Users only see documents from their department
- **Patient-specific access**: Doctors only see documents for their assigned patients
- **Sensitive document handling**: Special handling for confidential information

## 📊 **Monitoring & Analytics**

### **Embedding Status Tracking**
```bash
# Check embedding status for all documents
curl -X GET "http://localhost:8003/api/v1/documents/embedding-statuses" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### **Performance Metrics**
- **Retrieval accuracy**: How well the system finds relevant documents
- **Response quality**: User satisfaction with AI responses
- **Processing time**: How quickly documents are processed and queries are answered

## 🛠️ **Configuration & Customization**

### **Environment Variables**
```env
# Core RAG Configuration
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CONTEXT_LENGTH=8000
SIMILARITY_THRESHOLD=0.7
MAX_RESULTS=5
```

### **Customizing Chunking Strategy**
```python
# Adjust chunk size based on document type
if document_type == "research_paper":
    chunk_size = 1500  # Longer chunks for detailed content
elif document_type == "procedure":
    chunk_size = 500   # Shorter chunks for step-by-step procedures
```

### **Similarity Threshold Tuning**
```python
# Adjust based on your use case
if user_role == "doctor":
    similarity_threshold = 0.8  # Higher threshold for medical accuracy
elif user_role == "nurse":
    similarity_threshold = 0.6  # Lower threshold for broader context
```

## 🚀 **Best Practices**

### **1. Document Organization**
- **Use descriptive titles**: "Cardiology Guidelines 2024" vs "Document1"
- **Categorize properly**: Assign correct document types and departments
- **Keep content clean**: Remove formatting artifacts before upload

### **2. Query Optimization**
- **Be specific**: "diabetes type 2 treatment guidelines" vs "diabetes"
- **Use context**: Specify patient or department when relevant
- **Iterate**: Refine queries based on initial results

### **3. System Maintenance**
- **Monitor embedding status**: Ensure all documents are properly embedded
- **Regular updates**: Keep documents current and relevant
- **Performance monitoring**: Track query performance and user satisfaction

## 🔧 **Troubleshooting**

### **Common Issues**

#### **No Relevant Results**
- **Check similarity threshold**: Lower it to get more results
- **Verify document content**: Ensure documents contain relevant information
- **Review chunking**: Documents might be chunked inappropriately

#### **Slow Response Times**
- **Check embedding status**: Ensure all documents are embedded
- **Optimize queries**: Use more specific search terms
- **Monitor database performance**: Check pgvector index performance

#### **Authorization Errors**
- **Verify user permissions**: Check user role and department assignments
- **Review Oso policies**: Ensure authorization rules are correct
- **Check document metadata**: Verify department and patient assignments

## 🎯 **Next Steps**

Your RAG system is already production-ready! Here are some ways to enhance it further:

1. **📈 Add Analytics**: Track usage patterns and response quality
2. **🔄 Conversation Memory**: Remember previous interactions for better context
3. **🎯 Personalization**: Learn user preferences and adapt responses
4. **🚀 Performance Optimization**: Add caching and batch processing
5. **🔍 Advanced Search**: Implement hybrid search (vector + keyword)

## 📚 **Additional Resources**

- **API Documentation**: http://localhost:8003/docs
- **RAG Research**: Papers on retrieval-augmented generation
- **OpenAI Documentation**: Embedding and chat completion APIs
- **pgvector Documentation**: Vector similarity search in PostgreSQL

---

**Your RAG system is a powerful tool that combines the best of AI with your organization's knowledge. Use it wisely, and it will become an invaluable asset for your healthcare team!** 🏥✨
