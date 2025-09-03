# 🏥 Healthcare Support Portal

A **Secure, Efficient, and Reliable Agentic RAG Application** built with Python microservices, featuring role-based access control, vector search, and AI-powered document assistance for healthcare professionals.

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🚀 Quick Start](#-quick-start)
- [🧠 RAG System Guide](#-rag-system-guide)
- [🏗️ Architecture](#️-architecture)
- [🔧 Services](#-services)
- [📚 API Documentation](#-api-documentation)
- [🔐 Security](#-security)
- [📊 Usage Examples](#-usage-examples)
- [🛠️ Development](#️-development)
- [🚀 Deployment](#-deployment)
- [🔧 Troubleshooting](#-troubleshooting)
- [📖 Contributing](#-contributing)
- [📄 License](#-license)

## 🎯 Overview

The Healthcare Support Portal is a **production-ready RAG (Retrieval-Augmented Generation) application** that revolutionizes how healthcare professionals access and use knowledge. It combines the power of AI with your organization's documents to provide intelligent, contextual assistance.

### 🧠 What is RAG and Why It's Revolutionary

**RAG (Retrieval-Augmented Generation)** solves the biggest problems with traditional AI:

- **❌ Traditional AI**: Knowledge cutoff, hallucinations, no sources
- **✅ RAG**: Always current, factual responses, source transparency

### 🏥 Key Technologies

- **🔐 Security:** [Oso](https://osohq.com) for fine-grained authorization
- **🧠 AI/RAG:** [OpenAI](https://openai.com) for embeddings and chat completions
- **🔧 Observability:** [Galileo](https://galileo.ai) for observability and logging
- **🗄️ Database:** PostgreSQL with [pgvector](https://github.com/pgvector/pgvector) for vector similarity search
- **🐍 Backend:** [FastAPI](https://fastapi.tiangolo.com) microservices with [SQLAlchemy](https://sqlalchemy.org)
- **📦 Package Management:** [uv](https://github.com/astral-sh/uv) for fast Python package management
- **🏗️ Architecture:** Python microservices in a monorepo with uv workspaces

## 🚀 Quick Start

### 🎯 What You'll Build

In the next 10 minutes, you'll have a **complete RAG application** running locally that:

- 🤖 **Answers questions** using your uploaded documents (RAG)
- 🔐 **Secure access control** with roles (Doctor, Nurse, Admin) using Oso
- 📊 **AI monitoring & analytics** with Galileo observability
- 🏥 **Department-based document isolation** for healthcare compliance
- 🌐 **Modern web interface** for document upload and chat

**Perfect for**: Learning RAG, testing AI applications, healthcare document management

### 🤔 **New to RAG, Oso, or Galileo?** 

**🤖 What is RAG (Retrieval-Augmented Generation)?**
- Think of it as "AI + Your Documents"
- Instead of AI giving generic answers, it reads YOUR documents first
- Then gives accurate, sourced answers based on your content
- Example: Upload medical guidelines → Ask "What's the diabetes protocol?" → Get answer WITH sources

**🔐 What is Oso (Authorization)?**
- Controls who can see what (like hospital departments)
- Doctors see different documents than nurses
- Prevents unauthorized access to sensitive data
- Think: "Only cardiology staff can see cardiology documents"

**📊 What is Galileo (AI Observability)?**
- Monitors your AI system's performance
- Tracks what questions are asked, response quality, costs
- Helps you improve and debug AI applications
- Optional but helpful for production AI systems

---

### 📋 Prerequisites 

You'll need these tools installed on your computer:

| Tool | Version | Purpose | Installation |
|------|---------|---------|-------------|
| **Python** | 3.11+ | Backend services | [Download](https://python.org/downloads) |
| **Node.js** | 20.19.0+ | Frontend web app | [Download](https://nodejs.org) |
| **Docker** | Latest | Database & services | [Download](https://docker.com/get-started) |
| **Git** | Any | Clone repository | [Download](https://git-scm.com) |

**🔑 API Keys** (free accounts):
- **OpenAI API Key** → [Get here](https://platform.openai.com/api-keys) (Required for RAG)
- **Galileo Account** → [Sign up here](https://app.galileo.ai/sign-up) (Optional for monitoring)

#### 🔍 Quick Check - Verify Installation
```bash
# Run this to verify everything is installed
python3 --version    # Should show 3.11 or higher
node --version       # Should show v20.19.0 or higher  
docker --version     # Should show Docker version
git --version        # Should show Git version
echo "✅ Ready to proceed!"
```
```

---

## 🚀 **3-Step Setup** (10 minutes)

### Step 1: 📥 **Download & Setup**

```bash
# 1. Clone the repository
git clone https://github.com/rungalileo/sdk-examples.git
cd sdk-examples/python/rag/healthcare-support-portal

# OR clone just this example (if available):
# git clone --depth 1 --filter=blob:none --sparse https://github.com/rungalileo/sdk-examples.git
# cd sdk-examples && git sparse-checkout set python/rag/healthcare-support-portal

# 2. Run automated setup (installs everything)
./setup.sh
```

**What this does:**
- ✅ Installs Python dependencies with `uv`
- ✅ Installs frontend dependencies with `npm`
- ✅ Creates all configuration files
- ✅ Generates secure secret keys
- ✅ Sets up the database

---

### Step 2: 🔑 **Add Your OpenAI API Key**

🚨 **REQUIRED**: The RAG system needs OpenAI to work.

1. **Get your API key**: Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. **Copy your key** (starts with `sk-`)
3. **Add it to the configuration**:

```bash
# Open the RAG service configuration file
nano packages/rag/.env

# Find this line:
# OPENAI_API_KEY=sk-your-openai-api-key-here
# Replace with your actual key:
# OPENAI_API_KEY=sk-abcd1234your-real-key-here
```

💡 **Alternative**: Set as environment variable:
```bash
export OPENAI_API_KEY="sk-your-real-key-here"
```

🔒 **Optional - Add Galileo** (for AI monitoring):
1. Sign up at [galileo.ai](https://app.galileo.ai/sign-up)
2. Get your Galileo API key from the dashboard
3. Add to `packages/rag/.env`: `GALILEO_API_KEY=your-galileo-key`

---

### Step 3: 🎆 **Launch Everything**

```bash
# Start all services (database, backend, frontend)
./run_all.sh
```

**Wait 30 seconds**, then visit: **http://localhost:3000** 🎉

🔄 **Success Indicators** (you should see these):
```
✅ PostgreSQL Database (Port 5432)
✅ Oso Dev Server (Port 8080)
✅ Auth Service (Port 8001)
✅ Patient Service (Port 8002) 
✅ RAG Service (Port 8003)
✅ Frontend Service (Port 3000)

All services started!
🌐 Frontend: http://localhost:3000
```

📋 **What's running:**
- 🌐 **Web App**: http://localhost:3000 (main interface)
- 🤖 **RAG API**: http://localhost:8003/docs (upload docs, ask questions)
- 🔐 **Auth API**: http://localhost:8001/docs (user management)
- 🏥 **Patient API**: http://localhost:8002/docs (patient records)
- 🗄️ **Database**: PostgreSQL with vector search
- ⚖️ **Security**: Oso authorization server

---

## 🎉 **You're Ready!** - Try Your RAG System

### 👥 **Step 4a: Get Demo Users** (Optional)

```bash
# Create demo accounts with sample data
uv run python -m common.seed_data
```

**Demo Login Credentials:**
- 👨‍⚕️ Doctor: `dr_smith` / `secure_password`
- 👩‍⚕️ Nurse: `nurse_johnson` / `secure_password`  
- 👨‍💼 Admin: `admin_wilson` / `secure_password`

### 📄 **Step 4b: Test Document Upload & Chat**

1. **Via Web Interface** (easiest):
   - Go to http://localhost:3000
   - Login with demo credentials
   - Upload a PDF document
   - Ask questions about it!

2. **Via API** (for developers):
```bash
# First, get a JWT token by logging in
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "dr_smith@hospital.com", "password": "secure_password"}'

# Use the token to upload a document
curl -X POST "http://localhost:8003/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_FROM_ABOVE" \
  -F "file=@your_document.pdf" \
  -F "title=Medical Guidelines"

# Ask the RAG system a question
curl -X POST "http://localhost:8003/api/v1/chat/ask" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_FROM_ABOVE" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the treatment guidelines?"}'
```

### 🛑 **Stop Services**

```bash
# Stop all services when done
./stop_all.sh
```

---

## 🔧 **Quick Start Troubleshooting**

### 🚫 **Common Issues & Solutions**

| Problem | Solution |
|---------|----------|
| **"Port already in use"** | Run `./stop_all.sh` then try again |
| **"uv not found"** | Install with: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **"Docker not running"** | Start Docker Desktop application |
| **"OpenAI API error"** | Check your API key in `packages/rag/.env` |
| **"Permission denied"** | Run `chmod +x *.sh` to make scripts executable |
| **"Node.js version"** | Upgrade to Node.js 20.19.0+ from [nodejs.org](https://nodejs.org) |

### 📝 **Step-by-Step Debugging**

1. **Check if services are running**:
   ```bash
   # See what's using your ports
   lsof -i :3000,8001,8002,8003,5432,8080
   ```

2. **Check service logs**:
   ```bash
   # View logs for debugging
   tail -f logs/rag.log        # RAG service logs
   tail -f logs/auth.log       # Auth service logs
   tail -f logs/frontend.log   # Frontend logs
   ```

3. **Reset everything**:
   ```bash
   ./stop_all.sh               # Stop all services
   docker-compose down         # Stop database
   docker-compose up -d        # Restart database
   ./run_all.sh               # Restart services
   ```

### 🌐 **Still Having Issues?**

- **Check the detailed troubleshooting guide** in the full README below
- **Open an issue** on [GitHub](https://github.com/rungalileo/sdk-examples/issues)
- **Join the community** on [Discord](https://discord.gg/galileo) for help

---

## 🚀 **What's Next?**

Now that your RAG system is running, explore these features:

### 📋 **Immediate Next Steps**
1. **Upload your first document** at http://localhost:3000
2. **Try different user roles** (Doctor vs Nurse vs Admin permissions)
3. **Ask questions** and see how RAG finds answers in your docs
4. **Check the Galileo dashboard** (if you added the API key) for AI insights

### 🕰 **Learn More About the System**
- **🏥 [Architecture Guide](#-architecture)** - How the microservices work
- **🔐 [Security Features](#-security)** - Oso authorization deep-dive  
- **🤖 [RAG System Guide](#-rag-system-guide)** - How document search works
- **🛠️ [Development Guide](#-development)** - Customize and extend the system

### 🎆 **Production Deployment**
- **🚀 [Deployment Guide](#-deployment)** - Take your system live
- **🔧 [Configuration Options](#-environment-configuration)** - Advanced settings
- **📊 [Monitoring Setup](#-observability)** - Production monitoring

**🎉 Congratulations! You now have a production-ready RAG system running locally!**

## 🧠 RAG System Guide

### 🎯 What Your RAG System Can Do

Your RAG application provides **intelligent document management and AI-powered assistance**:

#### 🔍 **Intelligent Document Search**
- **Semantic search**: Find documents even without exact keywords
- **Department filtering**: Search within specific departments
- **Document type filtering**: Filter by guidelines, research, procedures
- **Similarity scoring**: Configurable relevance thresholds

#### 🤖 **AI-Powered Q&A**
- **Context-aware responses**: Uses relevant documents to inform answers
- **Role-based responses**: Tailored for doctors, nurses, administrators
- **Source attribution**: Shows which documents were used
- **Fallback handling**: Graceful responses when no context is found

#### 🔐 **Enterprise Security**
- **JWT authentication**: Secure user sessions
- **Oso authorization**: Fine-grained access control
- **Department isolation**: Users only see their department's documents
- **Audit trails**: Track all document access and modifications

### 🏗️ How RAG Works

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

#### **Step 1: Document Processing**
```
Upload Document → Text Extraction → Chunking → Embedding Generation → Vector Storage
```

#### **Step 2: Query Processing**
```
User Question → Query Embedding → Similarity Search → Context Retrieval
```

#### **Step 3: Response Generation**
```
Retrieved Context + User Role + Question → OpenAI GPT → Contextual Response
```

### 🎯 Real-World Use Cases

#### **🏥 For Doctors**
- **Query**: "What are the contraindications for prescribing metformin?"
- **RAG Response**: Uses latest medical guidelines and research papers to provide evidence-based information.

#### **👩‍⚕️ For Nurses**
- **Query**: "How do I properly administer insulin to a patient?"
- **RAG Response**: Uses nursing procedures and safety guidelines for step-by-step instructions.

#### **👨‍💼 For Administrators**
- **Query**: "What are the HIPAA compliance requirements for patient data?"
- **RAG Response**: Uses policy documents and compliance guidelines.

### 📚 RAG Documentation

- **🚀 [Quick Start Guide](packages/rag/QUICK_START.md)**: Get up and running in 5 minutes
- **📖 [Complete User Guide](packages/rag/RAG_GUIDE.md)**: Comprehensive usage instructions
- **🚀 [Enhancement Ideas](packages/rag/ENHANCEMENTS.md)**: Advanced features and improvements
- **📖 [RAG Summary](packages/rag/SUMMARY.md)**: Overview of capabilities

## 🏗️ Architecture

```
Healthcare Support Portal
├── 📦 packages/                  # Python workspace packages
│   ├── 🔐 auth/ (Port 8001)
│   │   ├── User authentication & JWT tokens
│   │   ├── User management & roles
│   │   └── Authorization policy enforcement
│   │
│   ├── 🏥 patient/ (Port 8002)
│   │   ├── Patient CRUD operations
│   │   ├── Doctor-patient assignments
│   │   └── Department-based filtering
│   │
│   ├── 🤖 rag/ (Port 8003)
│   │   ├── Document management & embeddings
│   │   ├── Vector similarity search
│   │   ├── AI-powered Q&A with context
│   │   └── File upload & processing
│   │
│   └── 📚 common/
│       ├── Shared models & database schema
│       ├── Authentication utilities
│       └── Pydantic schemas
│
├── 🌐 frontend/ (Port 3000)
│   └── React Router 7 + Vite web application
│
├── 🗄️ PostgreSQL + pgvector (Port 5432)
│   ├── User, Patient, Document tables
│   ├── Vector embeddings storage
│   └── Alembic migration tracking
│
├── 🔄 Migration Service (Docker)
│   ├── Alembic-based schema migrations
│   ├── Database health checks & retry logic
│   └── Automatic pgvector extension setup
│
├── ⚖️ Oso Dev Server (Port 8080)
│   ├── Centralized policy management
│   ├── Hot-reloading during development
│   └── Authorization policy enforcement
│
└── authorization.polar              # Oso authorization policies
```

## 🔧 Services

### 🔐 Auth Service (Port 8001)
**Purpose:** User authentication, authorization, and management

**Key Features:**
- JWT token generation and validation
- User registration with role assignment
- Token refresh and session management
- Oso policy enforcement for user access

**Endpoints:**
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Current user info
- `GET /api/v1/users/` - List users (with authorization)

[📖 Detailed Documentation](packages/auth/README.md)

### 🏥 Patient Service (Port 8002)
**Purpose:** Patient record management with role-based access

**Key Features:**
- Patient CRUD operations with authorization
- Doctor-patient assignment management
- Department-based filtering and search
- Soft delete for data preservation

**Endpoints:**
- `GET /api/v1/patients/` - List authorized patients
- `POST /api/v1/patients/` - Create new patient
- `GET /api/v1/patients/{id}` - Get patient details
- `PUT /api/v1/patients/{id}` - Update patient

[📖 Detailed Documentation](packages/patient/README.md)

### 🤖 RAG Service (Port 8003)
**Purpose:** AI-powered document management and intelligent assistance

**Key Features:**
- Document upload with automatic embedding generation
- Vector similarity search using pgvector
- Context-aware AI responses with OpenAI GPT
- Role-based AI behavior and document access

**Endpoints:**
- `POST /api/v1/documents/` - Create/upload documents
- `POST /api/v1/chat/search` - Semantic document search
- `POST /api/v1/chat/ask` - AI-powered Q&A
- `GET /api/v1/documents/` - List authorized documents

[📖 Detailed Documentation](packages/rag/README.md)

### 🌐 Frontend Application (Port 3000)
**Purpose:** Modern web interface for healthcare professionals

**Key Features:**
- React Router 7 with Vite for fast development
- shadcn/ui components for consistent design  
- TailwindCSS v4 for styling
- Real-time updates and responsive design
- Role-based UI components

**Technology Stack:**
- React Router 7 (Framework mode)
- Vite (Build tool)
- TypeScript
- TailwindCSS v4 (zero-config)
- shadcn/ui components

## 📚 API Documentation

Each service provides interactive API documentation:

| Service | Swagger UI | ReDoc |
|---------|------------|-------|
| Auth Service | http://localhost:8001/docs | http://localhost:8001/redoc |
| Patient Service | http://localhost:8002/docs | http://localhost:8002/redoc |
| RAG Service | http://localhost:8003/docs | http://localhost:8003/redoc |

## 🔐 Security

### 🔒 Authentication & Authorization
- **JWT-based authentication** with secure token management
- **Role-based access control** (Doctor, Nurse, Admin) using Oso policies
- **Fine-grained permissions** at the database level with SQLAlchemy integration
- **Department-based access controls** for multi-tenant healthcare environments

### 🛡️ Security Features
- **API Key Security:** OpenAI keys stored in environment variables
- **Content Filtering:** Sensitive document access controls
- **Audit Trail:** Document creation and access logging
- **Input Validation:** Sanitization of user inputs
- **Rate Limiting:** Protection against API abuse

## 📊 Usage Examples

### 1. Register and Authenticate

```bash
# Register a new doctor
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "secure_password",
    "role": "doctor",
    "department": "cardiology"
  }'

# Login to get JWT token
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "secure_password"
  }'
```

### 2. Upload Medical Documents

```bash
# Upload a medical guideline document
curl -X POST "http://localhost:8003/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@diabetes_guidelines.pdf" \
  -F "title=Diabetes Treatment Guidelines 2024" \
  -F "document_type=guidelines" \
  -F "department=endocrinology"
```

### 3. Search Documents

```bash
# Search for relevant documents
curl -X POST "http://localhost:8003/api/v1/chat/search" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "metformin contraindications",
    "document_types": ["guidelines"],
    "department": "endocrinology"
  }'
```

### 4. Ask AI Questions

```bash
# Ask an AI-powered question
curl -X POST "http://localhost:8003/api/v1/chat/ask" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the latest treatment guidelines for type 2 diabetes?",
    "context_department": "endocrinology"
  }'
```

### 5. Manage Patients

```bash
# Create a new patient
curl -X POST "http://localhost:8002/api/v1/patients/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "date_of_birth": "1980-01-15",
    "department": "cardiology",
    "assigned_doctor_id": 1
  }'
```

## 🛠️ Development

### Project Structure

```
healthcare-support-portal/
├── 📦 packages/                  # Python microservices
│   ├── 🔐 auth/                 # Authentication service
│   ├── 🏥 patient/              # Patient management service
│   ├── 🤖 rag/                  # RAG (AI) service
│   └── 📚 common/               # Shared utilities
├── 🌐 frontend/                 # React web application
├── 🗄️ data/                    # Database data
├── 📝 logs/                     # Service logs
├── 🔧 scripts/                  # Utility scripts
└── 📄 Configuration files
```

### Development Commands

```bash
# Install dependencies
uv sync

# Start development services
./run_all.sh

# Run database migrations
docker-compose run migrate

# Seed demo data
uv run python -m common.seed_data

# Stop all services
./stop_all.sh
```

### Environment Configuration

**🎯 Start with .env.example files!** Each service has its own `.env.example` file that contains all the configuration templates you need. This is the **recommended way** to set up your environment.

Each service has its own `.env` file for configuration. Here's how to set up all environment variables:

#### 🔐 Auth Service (packages/auth/.env)

```env
# Auth Service Environment Variables
DEBUG=true
SECRET_KEY=change-me-in-production
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare
ACCESS_TOKEN_EXPIRE_MINUTES=30
OSO_URL=http://localhost:8080
OSO_AUTH=e_0123456789_12345_osotesttoken01xiIn
```

#### 🏥 Patient Service (packages/patient/.env)

```env
# Patient Service Environment Variables
DEBUG=true
SECRET_KEY=change-me-in-production
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare
OSO_URL=http://localhost:8080
OSO_AUTH=e_0123456789_12345_osotesttoken01xiIn
```

#### 🤖 RAG Service (packages/rag/.env)

```env
# RAG Service Environment Variables
DEBUG=true
SECRET_KEY=change-me-in-production
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare
OSO_URL=http://localhost:8080
OSO_AUTH=e_0123456789_12345_osotesttoken01xiIn

# OpenAI Configuration (Required for RAG functionality)
OPENAI_API_KEY=sk-your-openai-api-key-here
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini

# RAG Configuration (Optional - has defaults)
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CONTEXT_LENGTH=8000
SIMILARITY_THRESHOLD=0.7
MAX_RESULTS=5

# Galileo Observability (Optional)
GALILEO_ENABLED=true
GALILEO_API_KEY=your-galileo-api-key-here
GALILEO_PROJECT_NAME=healthcare-rag
GALILEO_ENVIRONMENT=development


# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

#### 🌐 Frontend (frontend/.env)

```env
# API Configuration
VITE_API_BASE_URL=http://localhost
VITE_AUTH_SERVICE_PORT=8001
VITE_PATIENT_SERVICE_PORT=8002
VITE_RAG_SERVICE_PORT=8003

# App Configuration
VITE_APP_NAME="Healthcare Support Portal"
VITE_APP_VERSION="0.1.0"

# Development
VITE_DEBUG=true
```

### 🔧 Environment Variable Setup

#### 1. Create Environment Files

```bash
# Copy example files to create your .env files
cp packages/auth/.env.example packages/auth/.env
cp packages/patient/.env.example packages/patient/.env
cp packages/rag/.env.example packages/rag/.env
cp frontend/.env.example frontend/.env
```

**📋 What's in the .env.example files?**

The `.env.example` files contain **templates** with all the necessary configuration variables and their default values. When you copy them to `.env`, you get a complete starting point with:

- **🔑 Required variables** (like `OPENAI_API_KEY`, `SECRET_KEY`)
- **⚙️ Optional variables** with sensible defaults
- **📝 Clear comments** explaining what each variable does
- **🚀 Development-ready** configuration values

**💡 Pro tip:** Always check the `.env.example` files first to see what configuration options are available!

#### 2. Configure Required Variables

**🔑 OpenAI API Key (Required for RAG)**
```bash
# Get your OpenAI API key from: https://platform.openai.com/api-keys
# Then update the RAG service .env file:
nano packages/rag/.env
# Set: OPENAI_API_KEY=sk-your-actual-api-key-here
```

**📖 Understanding Your .env.example Files**

Each service has a comprehensive `.env.example` file. Here's what you'll find:

**🔐 Auth Service (.env.example)**
```bash
# View the template
cat packages/auth/.env.example

# Key variables:
# - SECRET_KEY: JWT signing key
# - DATABASE_URL: PostgreSQL connection string
# - ACCESS_TOKEN_EXPIRE_MINUTES: JWT expiration time
# - OSO_URL: Authorization service URL
```

**🏥 Patient Service (.env.example)**
```bash
# View the template
cat packages/patient/.env.example

# Key variables:
# - SECRET_KEY: Service authentication key
# - DATABASE_URL: PostgreSQL connection string
# - OSO_URL: Authorization service URL
```

**🤖 RAG Service (.env.example)**
```bash
# View the template
cat packages/rag/.env.example

# Key variables:
# - OPENAI_API_KEY: Your OpenAI API key (required)
# - EMBEDDING_MODEL: AI model for document embeddings
# - CHAT_MODEL: AI model for Q&A responses
# - GALILEO_ENABLED: Observability platform toggle
# - LOG_LEVEL: Logging verbosity
```

**🔐 Security Keys (Required for Production)**
```bash
# Generate secure secret keys for production
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update all service .env files with unique secret keys:
nano packages/auth/.env
nano packages/patient/.env
nano packages/rag/.env
# Set: SECRET_KEY=your-generated-secret-key
```

**🔍 Quick Configuration Check**

After copying your `.env.example` files, you can quickly see what needs to be configured:

```bash
# Check what variables need your attention
echo "=== Checking required configuration ==="
echo "OpenAI API Key:"
grep "OPENAI_API_KEY" packages/rag/.env
echo ""
echo "Secret Keys:"
grep "SECRET_KEY" packages/*/.env
echo ""
echo "Database URLs:"
grep "DATABASE_URL" packages/*/.env

# Look for placeholder values that need updating
echo ""
echo "=== Placeholder values to update ==="
grep -r "change-me\|your-\|sk-" packages/*/.env
```

**🗄️ Database Configuration**
```env
# Default development database URL (PostgreSQL with pgvector)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare

# For production, use your actual database URL:
# DATABASE_URL=postgresql+psycopg2://user:password@host:port/database
```

#### 3. Optional Configuration

**🔍 RAG System Tuning**
```env
# Adjust these values based on your needs:

# Embedding Model (OpenAI models)
EMBEDDING_MODEL=text-embedding-3-small    # Fast, cost-effective
# EMBEDDING_MODEL=text-embedding-3-large  # Higher accuracy, more expensive

# Chat Model (OpenAI models)
CHAT_MODEL=gpt-4o-mini    # Fast, cost-effective
# CHAT_MODEL=gpt-4o       # Higher quality responses

# Document Processing
CHUNK_SIZE=1000           # Characters per chunk
CHUNK_OVERLAP=200         # Overlap between chunks
MAX_CONTEXT_LENGTH=8000   # Max tokens for AI context

# Search Configuration
SIMILARITY_THRESHOLD=0.7  # Minimum similarity score (0.0-1.0)
MAX_RESULTS=5             # Maximum search results
```

**⏱️ Token Expiration**
```env
# Auth service token expiration (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Default: 30 minutes
```

**🔐 Oso Authorization**
```env
# Development (local Oso server)
OSO_URL=http://localhost:8080
OSO_AUTH=e_0123456789_12345_osotesttoken01xiIn

# Production (Oso Cloud)
# OSO_URL=https://cloud.osohq.com
# OSO_AUTH=your-production-oso-api-key
```

### 🚀 Quick Environment Setup

For quick development setup, you can use these commands:

```bash
# 1. Copy all example files
cp packages/auth/.env.example packages/auth/.env
cp packages/patient/.env.example packages/patient/.env
cp packages/rag/.env.example packages/rag/.env
cp frontend/.env.example frontend/.env

# 2. Update your OpenAI API key (required for RAG)
# Edit packages/rag/.env and set your actual OpenAI API key:
# OPENAI_API_KEY=sk-your-actual-api-key-here

# 3. Generate secure secret keys
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
echo "SECRET_KEY=$SECRET_KEY" >> packages/auth/.env
echo "SECRET_KEY=$SECRET_KEY" >> packages/patient/.env
echo "SECRET_KEY=$SECRET_KEY" >> packages/rag/.env

# 4. Start services
./run_all.sh
```

## 🚀 Deployment

### Production Deployment

#### 1. **Production Environment Variables**

Create production-specific `.env` files with secure values:

**🔐 Auth Service (packages/auth/.env)**
```env
DEBUG=false
SECRET_KEY=your-super-secure-64-character-secret-key
DATABASE_URL=postgresql+psycopg2://user:password@prod-db:5432/healthcare
ACCESS_TOKEN_EXPIRE_MINUTES=30
OSO_URL=https://cloud.osohq.com
OSO_AUTH=your-production-oso-cloud-api-key
```

**🏥 Patient Service (packages/patient/.env)**
```env
DEBUG=false
SECRET_KEY=your-super-secure-64-character-secret-key
DATABASE_URL=postgresql+psycopg2://user:password@prod-db:5432/healthcare
OSO_URL=https://cloud.osohq.com
OSO_AUTH=your-production-oso-cloud-api-key
```

**🤖 RAG Service (packages/rag/.env)**
```env
DEBUG=false
SECRET_KEY=your-super-secure-64-character-secret-key
DATABASE_URL=postgresql+psycopg2://user:password@prod-db:5432/healthcare
OSO_URL=https://cloud.osohq.com
OSO_AUTH=your-production-oso-cloud-api-key

# OpenAI Configuration
OPENAI_API_KEY=sk-your-production-openai-api-key
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CONTEXT_LENGTH=8000
SIMILARITY_THRESHOLD=0.7
MAX_RESULTS=5

# Galileo Observability
GALILEO_ENABLED=true
GALILEO_API_KEY=your-production-galileo-api-key
GALILEO_PROJECT_NAME=healthcare-rag-prod
GALILEO_ENVIRONMENT=production


# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**🌐 Frontend (frontend/.env)**
```env
# API Configuration
VITE_API_BASE_URL=https://your-domain.com
VITE_AUTH_SERVICE_PORT=8001
VITE_PATIENT_SERVICE_PORT=8002
VITE_RAG_SERVICE_PORT=8003

# App Configuration
VITE_APP_NAME="Healthcare Support Portal"
VITE_APP_VERSION="1.0.0"

# Production
VITE_DEBUG=false
```

#### 2. **Security Checklist**

- ✅ **Generate unique secret keys** for each service
- ✅ **Use HTTPS** for all production URLs
- ✅ **Configure Oso Cloud** instead of local Oso server
- ✅ **Set DEBUG=false** for all services
- ✅ **Use production database** with proper credentials
- ✅ **Configure CORS** for your domain
- ✅ **Set up monitoring** and logging
- ✅ **Enable rate limiting** and request throttling

#### 3. **Database Migration**
```bash
# Run migrations on production database
docker-compose run migrate
```

#### 4. **Service Deployment**
```bash
# Deploy services (example with Docker)
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual services
docker build -f Dockerfile.auth -t auth-service .
docker build -f Dockerfile.patient -t patient-service .
docker build -f Dockerfile.rag -t rag-service .
```

## 🔧 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check if ports are available
lsof -i :8001
lsof -i :8002
lsof -i :8003
lsof -i :3000

# Check service logs
tail -f logs/auth.log
tail -f logs/patient.log
tail -f logs/rag.log
```

#### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs healthcare-support-portal-postgres-1

# Test database connection
uv run python -c "from common.db import get_db; print('DB connection OK')"
```

#### Environment Variable Issues
```bash
# Check if .env files exist
ls -la packages/*/.env
ls -la frontend/.env

# Verify environment variables are loaded
cd packages/auth && source .env && env | grep -E "(DEBUG|SECRET_KEY|DATABASE_URL)"
cd packages/patient && source .env && env | grep -E "(DEBUG|SECRET_KEY|DATABASE_URL)"
cd packages/rag && source .env && env | grep -E "(DEBUG|SECRET_KEY|OPENAI_API_KEY)"

# Check for missing required variables
grep -r "OPENAI_API_KEY" packages/rag/.env
grep -r "SECRET_KEY" packages/*/.env
```

#### OpenAI API Errors
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test OpenAI connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# Check if API key is in .env file
grep "OPENAI_API_KEY" packages/rag/.env
```

#### RAG System Issues
```bash
# Check embedding status
curl -X GET "http://localhost:8003/api/v1/documents/embedding-statuses" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Regenerate embeddings if needed
curl -X POST "http://localhost:8003/api/v1/documents/{doc_id}/regenerate-embeddings" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Debug Mode

Set `DEBUG=true` for detailed logging:
- Embedding generation logs
- Vector search query details
- AI response generation steps
- Authorization decision logging

## 📖 Contributing

### Development Guidelines

1. **Follow existing patterns** for async/await operations
2. **Add comprehensive error handling** for external API calls
3. **Update vector search logic** carefully to maintain performance
4. **Test with various document types** and sizes
5. **Consider cost implications** of AI model changes
6. **Update documentation** for new features

### Code Style

- Use **async/await** for AI operations
- Follow **FastAPI** best practices
- Implement **proper error handling**
- Add **comprehensive logging**
- Write **clear documentation**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 **Your RAG System is Ready!**

You now have a **world-class RAG application** that can transform how your organization accesses and uses knowledge. 

### 🔧 **Important Configuration Notes**

- **🔑 OpenAI API Key**: Required for RAG functionality - get yours at [OpenAI Platform](https://platform.openai.com/api-keys)
- **🔐 Security Keys**: Generate unique secret keys for each service in production
- **🗄️ Database**: Ensure PostgreSQL with pgvector extension is running
- **🔍 Environment Files**: Each service has its own `.env` file for configuration
- **📊 Galileo**: Observability platform for monitoring and analytics

### 🚀 **Next Steps**

1. **📖 [RAG Quick Start Guide](packages/rag/QUICK_START.md)**: Get up and running in 5 minutes
2. **📚 [Complete RAG Guide](packages/rag/RAG_GUIDE.md)**: Master all RAG features
3. **🔧 Configure Environment**: Set up all required environment variables
4. **🧪 Test Your System**: Upload documents and ask questions
5. **🚀 Deploy to Production**: Follow the production deployment guide

### 📋 **Configuration Checklist**

- ✅ **Environment files created** for all services
- ✅ **OpenAI API key configured** in RAG service
- ✅ **Secret keys generated** for all services
- ✅ **Database connection** working
- ✅ **All services starting** without errors
- ✅ **RAG functionality** tested with document upload and query
- ✅ **Galileo observability** configured (optional)
- ✅ **Prometheus metrics** accessible at `/metrics` endpoint

**Welcome to the future of intelligent knowledge management!** 🏥✨

