# 🏥 Healthcare Support Portal

A **Secure, Efficient, and Reliable Agentic RAG Application** built with Python microservices, featuring role-based access control, vector search, and AI-powered document assistance for healthcare professionals.

## 📋 Table of Contents

### 🚀 Getting Started
- [🎯 What You'll Build](#-what-youll-build)
- [📋 Prerequisites](#-prerequisites) 
- [⚡ Quick Setup (15 min)](#-quick-setup)
- [🔍 Validation & Testing](#-validation--testing)

### 🏥 For Healthcare Organizations
- [🏥 Healthcare Team Guide](#-healthcare-team-guide)
- [🔐 Security & Compliance](#-security--compliance)
- [👥 Team Onboarding](#-team-onboarding)

### 💻 Technical Documentation
- [🧠 RAG System Guide](#-rag-system-guide)
- [🏗️ Architecture](#️-architecture)
- [🔧 Services](#-services)
- [📚 API Documentation](#-api-documentation)
- [🛠️ Development](#️-development)
- [🚀 Deployment](#-deployment)

### 🆘 Support & Troubleshooting
- [🔧 Troubleshooting Guide](#-troubleshooting-guide)
- [📞 Getting Help](#-getting-help)
- [📖 Contributing](#-contributing)
- [📄 License](#-license)

## 🎯 What You'll Build



In the next **15 minutes**, you'll deploy a complete **healthcare-grade AI knowledge management system** that transforms how medical teams access information:

### 🏥 **Real-World Healthcare Scenarios**

**👩‍⚕️ For Doctors:**
- *"What are the contraindications for prescribing metformin to elderly patients?"*
- **AI Response:** Searches your uploaded medical guidelines and research papers to provide evidence-based, sourced answers with specific page references.

**👩‍⚕️ For Nurses:**
- *"Show me the step-by-step protocol for insulin administration in ICU patients"*
- **AI Response:** Retrieves department-specific procedures with safety checklists and dosage calculations.

**👨‍💼 For Administrators:**
- *"What are our HIPAA requirements for patient data backup?"*
- **AI Response:** Cites relevant policy documents and compliance frameworks.

### 🚀 **What Makes This Special**

| Feature | Traditional Search | Healthcare Support Portal |
|---------|-------------------|---------------------------|
| **Accuracy** | Keyword matching | AI understands context & medical terminology |
| **Security** | Basic permissions | Role-based access (Doctor/Nurse/Admin) + audit trails |
| **Sources** | No attribution | Every answer shows exact document sources |
| **Knowledge** | Static documents | AI synthesizes information from multiple sources |
| **Compliance** | Manual tracking | Built-in HIPAA-conscious design patterns |

### 🧠 **The RAG Revolution in Healthcare**

**Traditional AI Problems:**
- ❌ Knowledge cutoff dates ("I don't know about 2024 guidelines")
- ❌ Hallucinations (making up medical facts)
- ❌ No source verification
- ❌ Generic responses

**RAG Solution:**
- ✅ **Always Current:** Uses YOUR latest medical documents
- ✅ **Factual:** Only uses information from uploaded sources
- ✅ **Transparent:** Shows exactly which documents were referenced
- ✅ **Contextual:** Tailored responses based on user role and department

### 🏗️ **Technical Foundation**

- **🔐 Security:** [Oso](https://osohq.com) - Hospital-grade authorization with role isolation
- **🧠 AI/RAG:** [OpenAI](https://openai.com) - Medical-grade embeddings and reasoning
- **📊 Observability:** [Galileo](https://galileo.ai) - AI performance monitoring and compliance tracking
- **🗄️ Database:** PostgreSQL + [pgvector](https://github.com/pgvector/pgvector) - HIPAA-ready with semantic search
- **🐍 Backend:** [FastAPI](https://fastapi.tiangolo.com) microservices - Production-ready with automatic API docs
- **📦 Package Management:** [uv](https://github.com/astral-sh/uv) - Fast, reliable Python dependency management

## 📋 Prerequisites


### 🔧 **System Requirements**

| Component | Minimum | Recommended | Purpose |
|-----------|---------|-------------|----------|
| **Python** | 3.11+ | 3.12+ | Backend services & AI processing |
| **Node.js** | 20.19.0+ | 22.0+ | React frontend application |
| **Docker** | 20.0+ | Latest | PostgreSQL + microservices |
| **RAM** | 8GB | 16GB+ | AI embeddings + database |
| **Storage** | 5GB free | 10GB+ | Documents + embeddings |

### 🔑 **API Keys** 

| Service | Required | Purpose | Cost |
|---------|----------|---------|------|
| **OpenAI** | ✅ **Yes** | AI embeddings & responses | ~$0.10-0.50/day testing |
| **Galileo** | ⭕ Optional | AI performance monitoring | Free tier available |

🔗 **Get your keys:**
- **OpenAI:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys) 
- **Galileo:** [app.galileo.ai/sign-up](https://app.galileo.ai/sign-up)

### 🔍 **Environment Validation**

**Step 1: Check Dependencies**
```bash
# Run this validation script
echo "🔍 Validating environment..."
python3 --version && echo "✅ Python OK" || echo "❌ Install Python 3.11+"
node --version && echo "✅ Node.js OK" || echo "❌ Install Node.js 20.19.0+"
docker --version && echo "✅ Docker OK" || echo "❌ Install Docker"
git --version && echo "✅ Git OK" || echo "❌ Install Git"

# Check available ports
echo "🔍 Checking port availability..."
for port in 3000 8001 8002 8003 5432; do
  if ! lsof -i :$port > /dev/null 2>&1; then
    echo "✅ Port $port available"
  else
    echo "⚠️  Port $port in use - you may need to stop other services"
  fi
done

echo "🎉 Environment validation complete!"
```

**Expected Output:**
```bash
✅ Python 3.11.9 OK
✅ Node.js v20.19.0 OK  
✅ Docker 24.0.7 OK
✅ Git 2.40.0 OK
✅ Port 3000 available
✅ Port 8001 available
✅ Port 8002 available
✅ Port 8003 available
✅ Port 5432 available
🎉 Environment validation complete!
```

> ⚠️ **Troubleshooting:** If any checks fail, see our [Environment Setup Guide](#-environment-setup-troubleshooting) below.

---

## ⚡ Quick Setup (15 min)


### **Step 1: Download & Install** ⏱️ *3 minutes*

```bash
# 1. Clone the repository
git clone https://github.com/rungalileo/sdk-examples.git
cd sdk-examples/python/rag/healthcare-support-portal

# 2. Run automated setup
chmod +x setup.sh
./setup.sh
```

**🔍 Validation:** You should see:
```bash
✅ Python dependencies synced
✅ Created packages/auth/.env from example
✅ Created packages/patient/.env from example  
✅ Created packages/rag/.env from example
✅ Updated SECRET_KEY in packages/auth/.env
✅ Frontend dependencies installed successfully
✅ Setup complete!
```

### **Step 2: Configure API Keys** ⏱️ *2 minutes*

**🎨 Critical:** The RAG system requires your OpenAI API key to function.

```bash
# Open the RAG service configuration
nano packages/rag/.env
# Or use your preferred editor: code packages/rag/.env
```

**Find this line:**
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Replace with your actual key:**
```env
OPENAI_API_KEY=sk-abcd1234your-real-key-here
```

**🔍 Validation:** Test your API key:
```bash
# Quick API key test
cd packages/rag
uv run python -c "import os; print('✅ API key configured' if os.getenv('OPENAI_API_KEY', '').startswith('sk-') else '❌ Invalid API key format')"
```

**Add Galileo for AI observability and monitoring:**
1. Get your Galileo API key from [app.galileo.ai](https://app.galileo.ai)
2. Add to `packages/rag/.env`: `GALILEO_API_KEY=your-galileo-key`
3. Test: `uv run python test_config.py`


### **Step 3: Launch All Services** ⏱️ *5 minutes*

```bash
# Start database, backend services, and frontend
./run_all.sh
```

**🔍 Watch for Success Indicators:**
```bash
✅ PostgreSQL Database (Port 5432)
✅ Oso Dev Server (Port 8080) 
✅ Auth Service (Port 8001)
✅ Patient Service (Port 8002)
✅ RAG Service (Port 8003)
✅ Frontend Service (Port 3000)

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
# Health check for all services
echo "🔍 Running system health check..."

# Check if all services are responding
echo "Testing Auth Service..."
curl -s http://localhost:8001/health && echo "✅ Auth Service OK" || echo "❌ Auth Service DOWN"

echo "Testing Patient Service..."
curl -s http://localhost:8002/health && echo "✅ Patient Service OK" || echo "❌ Patient Service DOWN"

echo "Testing RAG Service..."
curl -s http://localhost:8003/health && echo "✅ RAG Service OK" || echo "❌ RAG Service DOWN"

echo "Testing Frontend..."
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend OK" || echo "❌ Frontend DOWN"

echo "Testing Database..."
docker exec healthcare-support-portal-postgres-1 pg_isready && echo "✅ Database OK" || echo "❌ Database DOWN"

echo "🎉 Health check complete!"
```

### **Step 5: Create Demo Users & Test RAG** ⏱️ *5 minutes*

**5a. Setup Demo Data:**
```bash
# Create sample users and data
uv run python -m common.seed_data
```

**🔍 Expected Output:**
```bash
✅ Created demo users:
   - Doctor: dr_smith@hospital.com / secure_password  
   - Nurse: nurse_johnson@hospital.com / secure_password
   - Admin: admin_wilson@hospital.com / secure_password
✅ Sample patients created
✅ Demo data seeding complete
```

**5b. Test the Web Interface:**
1. 🌐 Open **http://localhost:3000**
2. 🔑 Login with: `dr_smith@hospital.com` / `secure_password`
3. 📄 Upload a PDF document (medical guideline, research paper, etc.)
4. 🤖 Ask a question: *"What are the key recommendations in this document?"*
5. ✅ Verify you get an AI response with document sources!

**5c. Test RAG API (Advanced):**
```bash
# Get authentication token
TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "dr_smith@hospital.com", "password": "secure_password"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Got auth token: ${TOKEN:0:20}..."

# Test document upload
echo "Testing document upload..."
curl -X POST "http://localhost:8003/api/v1/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@README.md" \
  -F "title=Test Document" && echo "✅ Upload successful"

# Test RAG query
echo "Testing RAG question-answering..."
curl -X POST "http://localhost:8003/api/v1/chat/ask" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is this application about?"}' && echo "✅ RAG response received"
```

### 🎉 **Success! Your Healthcare RAG System is Running**

**🌐 Access Points:**
- **Main Application:** http://localhost:3000
- **Auth API Docs:** http://localhost:8001/docs  
- **Patient API Docs:** http://localhost:8002/docs
- **RAG API Docs:** http://localhost:8003/docs
- **Oso Authorization:** http://localhost:8080

**👥 Demo Accounts:**
| Role | Email | Password | Department | Permissions |
|------|--------|----------|------------|-------------|
| Doctor | `dr_smith@hospital.com` | `secure_password` | Cardiology | Full access to cardiology docs |
| Nurse | `nurse_johnson@hospital.com` | `secure_password` | Emergency | Access to procedures & protocols |
| Admin | `admin_wilson@hospital.com` | `secure_password` | Administration | System-wide access |

**🛑 To Stop Services:**
```bash
./stop_all.sh
```

**➡️ What's Next?**
- [🏥 Healthcare Team Guide](#-healthcare-team-guide) - Role-specific usage patterns
- [🔧 Troubleshooting Guide](#-troubleshooting-guide) - Common issues & solutions  
- [🔐 Security & Compliance](#-security--compliance) - HIPAA considerations
- [🛠️ Development Guide](#-development) - Customize and extend

---

---

## 🔧 Troubleshooting Guide

<details>
<summary><strong>🚑 Quick Fixes for Common Issues</strong></summary>

### 📝 **Decision Tree: What's Wrong?**

```
🚨 Having issues? Follow this decision tree:

🔍 Is the system not starting?
├── ❌ Ports in use? → Run `./stop_all.sh` then `./run_all.sh`
├── ❌ Docker not running? → Start Docker Desktop
├── ❌ "uv not found"? → Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
└── ❌ Dependencies missing? → Run `./setup.sh` again

🔍 Services start but RAG doesn't work?
├── ❌ "OpenAI API error"? → Check API key in `packages/rag/.env`
├── ❌ "Invalid API key"? → Ensure key starts with `sk-`
└── ❌ "Galileo span error"? → See Galileo troubleshooting below

🔍 Frontend not loading?
├── ❌ Node.js version? → Upgrade to 20.19.0+ from nodejs.org
└── ❌ Dependencies? → Run `cd frontend && npm install`
```

</details>

### 📝 **Environment Setup Troubleshooting**

<details>
<summary><strong>Python, Node.js, Docker Issues</strong></summary>

**🐍 Python Issues:**
```bash
# Check Python version
python3 --version

# If Python < 3.11, install newer version:
# macOS: brew install python@3.12
# Ubuntu: sudo apt install python3.12
# Windows: Download from python.org

# Verify uv installation
which uv || curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell after uv install
source ~/.bashrc  # or ~/.zshrc
```

**💻 Node.js Issues:**
```bash
# Check Node version
node --version

# If version < 20.19.0:
# Install Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc

# Install and use Node 20+
nvm install 20
nvm use 20

# Verify npm is working
npm --version
```

**🐳 Docker Issues:**
```bash
# Check if Docker is running
docker ps

# Start Docker (varies by OS)
# macOS: Open Docker Desktop
# Linux: sudo systemctl start docker
# Windows: Start Docker Desktop

# Test Docker
docker run hello-world
```

</details>

### 🔑 **API Key & Configuration Issues**

<details>
<summary><strong>OpenAI, Galileo, Environment Variables</strong></summary>

**🤖 OpenAI API Key Problems:**
```bash
# Check if API key is set
grep "OPENAI_API_KEY" packages/rag/.env

# Key should look like: OPENAI_API_KEY=sk-abcd1234...
# If missing 'sk-' prefix, it's invalid

# Test API key manually
export OPENAI_API_KEY="your-key-here"
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models | head -20

# Should return JSON with model list, not error
```

**📊 Galileo "Span Error" Fix:**
```bash
# The "add_workflow_span: A trace needs to be created" error is non-fatal
# It means Galileo monitoring is enabled but not properly initialized

# Option 1: Disable Galileo (simplest)
echo "GALILEO_ENABLED=false" >> packages/rag/.env

# Option 2: Fix Galileo setup
echo "GALILEO_API_KEY=your-galileo-key" >> packages/rag/.env
echo "GALILEO_PROJECT_NAME=healthcare-rag" >> packages/rag/.env

# Option 3: Test Galileo connection
cd packages/rag
uv run python test_config.py
```

**🔒 Environment Variable Debug:**
```bash
# Check all .env files exist
ls -la packages/*/.env

# View environment variables (without exposing keys)
echo "Checking environment configuration..."
for service in auth patient rag; do
  echo "=== $service service ==="
  grep -v "API_KEY\|SECRET" packages/$service/.env || echo "No .env file"
done

# Generate new SECRET_KEY if needed
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

</details>

### 🛠️ **Service & Port Issues**

<details>
<summary><strong>Services Won't Start, Port Conflicts</strong></summary>

**📋 Port Conflict Resolution:**
```bash
# Find what's using required ports
echo "Checking port usage..."
for port in 3000 8001 8002 8003 5432 8080; do
  process=$(lsof -ti:$port 2>/dev/null)
  if [ -n "$process" ]; then
    echo "⚠️  Port $port used by PID $process:"
    ps -p $process -o pid,ppid,cmd
  else
    echo "✅ Port $port available"
  fi
done

# Kill processes on our ports (be careful!)
echo "Kill conflicting processes? (y/N)"
read answer
if [ "$answer" = "y" ]; then
  for port in 3000 8001 8002 8003; do
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
  done
fi
```

**📊 Service Health Debugging:**
```bash
# Check individual service logs
echo "Recent service logs:"
echo "=== RAG Service ==="
tail -20 logs/rag.log

echo "=== Auth Service ==="
tail -20 logs/auth.log

echo "=== Frontend ==="
tail -20 logs/frontend.log

# Test services individually
echo "Testing service endpoints:"
curl -s http://localhost:8001/docs > /dev/null && echo "✅ Auth API responding" || echo "❌ Auth API down"
curl -s http://localhost:8003/docs > /dev/null && echo "✅ RAG API responding" || echo "❌ RAG API down"
```

**🗄️ Database Issues:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs healthcare-support-portal-postgres-1

# Test database connection
docker exec healthcare-support-portal-postgres-1 \
  psql -U postgres -d healthcare -c "\\dt" 2>/dev/null && \
  echo "✅ Database tables exist" || echo "❌ Database connection failed"

# Reset database (nuclear option)
echo "Reset database? This will delete all data! (y/N)"
read answer
if [ "$answer" = "y" ]; then
  docker-compose down
  docker volume rm healthcare-support-portal_postgres_data 2>/dev/null || true
  docker-compose up -d db
  sleep 5
  docker-compose run --rm migrate
fi
```

</details>

### 🧠 **RAG System Issues**

<details>
<summary><strong>Document Upload, Embeddings, AI Responses</strong></summary>

**📄 Document Upload Problems:**
```bash
# Test document upload with curl
TOKEN="your-jwt-token-here"

# Upload test document
echo "Testing document upload..."
response=$(curl -s -w "%{http_code}" -X POST "http://localhost:8003/api/v1/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@README.md" \
  -F "title=Test Document")

echo "Upload response: $response"

# Check upload status
curl -s "http://localhost:8003/api/v1/documents/" \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys,json; print(f'Documents: {len(json.load(sys.stdin))}')"
```

**🤖 AI Response Issues:**
```bash
# Test RAG question directly
TOKEN="your-jwt-token-here"

# Simple test query
echo "Testing RAG query..."
curl -X POST "http://localhost:8003/api/v1/chat/ask" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, are you working?"}'

# Check embedding generation
echo "Checking embedding status..."
curl -s "http://localhost:8003/api/v1/documents/" \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "
import sys,json
data = json.load(sys.stdin)
for doc in data:
    status = 'embedded' if doc.get('embedding_id') else 'no embedding'
    print(f'{doc[\"title\"]}: {status}')
"
```

**📈 Performance Issues:**
```bash
# Check system resources
echo "System resources:"
echo "RAM usage: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo "Disk usage: $(df -h . | tail -1 | awk '{print $3"/"$2" ("$5" used)"}')"

# Check Docker resources
echo "Docker stats:"
docker stats --no-stream

# Monitor RAG service performance
echo "Monitoring RAG API response times..."
for i in {1..5}; do
  start=$(date +%s.%N)
  curl -s "http://localhost:8003/health" > /dev/null
  end=$(date +%s.%N)
  echo "Response $i: $(echo "$end - $start" | bc -l)s"
  sleep 1
done
```

</details>

### 🎨 **Complete System Reset**

<details>
<summary><strong>Nuclear Option: Fresh Start</strong></summary>

```bash
#!/bin/bash
echo "🚨 COMPLETE SYSTEM RESET - This will delete all data!"
echo "Continue? (type 'RESET' to confirm)"
read confirm

if [ "$confirm" = "RESET" ]; then
  echo "Stopping all services..."
  ./stop_all.sh
  
  echo "Removing containers and volumes..."
  docker-compose down --volumes --remove-orphans
  
  echo "Cleaning up logs and data..."
  rm -rf logs/*
  rm -rf data/postgres/*
  
  echo "Removing environment files..."
  rm -f packages/*/.env
  
  echo "Cleaning Python environment..."
  rm -rf .venv
  
  echo "Cleaning Node modules..."
  rm -rf frontend/node_modules
  
  echo "Starting fresh setup..."
  ./setup.sh
  
  echo "✅ Fresh installation complete!"
  echo "Don't forget to add your OpenAI API key to packages/rag/.env"
else
  echo "Reset cancelled."
fi
```

**Save this as `reset.sh`, make executable with `chmod +x reset.sh`, then run `./reset.sh`**

</details>

### 📞 Getting Help

**🔍 Before Asking for Help, Collect This Info:**
```bash
# Run this diagnostic script
echo "=== Healthcare RAG System Diagnostics ==="
echo "OS: $(uname -s) $(uname -r)"
echo "Python: $(python3 --version)"
echo "Node: $(node --version 2>/dev/null || echo 'Not installed')"
echo "Docker: $(docker --version 2>/dev/null || echo 'Not installed')"
echo "uv: $(uv --version 2>/dev/null || echo 'Not installed')"
echo ""
echo "Port Status:"
for port in 3000 8001 8002 8003 5432; do
  lsof -i :$port > /dev/null 2>&1 && echo "Port $port: IN USE" || echo "Port $port: Available"
done
echo ""
echo "Service Status:"
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "Environment Files:"
ls -la packages/*/.env 2>/dev/null || echo "No .env files found"
echo ""
echo "Recent Errors (last 10 lines from each log):"
for log in logs/*.log; do
  if [ -f "$log" ]; then
    echo "=== $(basename $log) ==="
    tail -10 "$log" | grep -i error || echo "No recent errors"
  fi
done
```

**🔗 Community Support:**
- **GitHub Issues:** [sdk-examples/issues](https://github.com/rungalileo/sdk-examples/issues)
- **Galileo Documentation:** [Galileo Docs](https://v2docs.galileo.ai)
- **Oso Support:** [Oso Documentation](https://docs.osohq.com)


---

## Example use cases

### 👩‍⚕️ **For Medical Professionals**

**🎯 Why This Matters for Healthcare:**
- **🚑 Emergency Response:** Get instant access to protocols during critical situations
- **📊 Evidence-Based Care:** AI responses include source citations for clinical decisions
- **🗺️ Department Isolation:** Only see documents relevant to your specialty
- **📋 Compliance Ready:** Built-in audit trails and access controls

#### **👨‍⚕️ Doctor Workflow**
1. **Upload Clinical Guidelines:**
   - Latest treatment protocols
   - Research papers and meta-analyses
   - Drug interaction databases
   - Departmental procedures

2. **Ask Clinical Questions:**
   - *"What are the contraindications for ACE inhibitors in elderly patients?"*
   - *"Show me the latest guidelines for diabetes management"*
   - *"What's the recommended antibiotic for pneumonia in immunocompromised patients?"*

3. **Get Sourced Answers:**
   - AI provides evidence-based responses
   - Shows exact page/section references
   - Highlights key recommendations
   - Flags any conflicting information

#### **👩‍⚕️ Nurse Workflow**
1. **Upload Procedure Documents:**
   - Nursing protocols and checklists
   - Medication administration guides
   - Patient care standards
   - Safety procedures

2. **Quick Procedure Lookup:**
   - *"How do I properly administer insulin via IV?"*
   - *"What's the protocol for fall risk assessment?"*
   - *"Show me the steps for wound care documentation"*

3. **Safety-First Responses:**
   - Step-by-step procedures with safety checkpoints
   - Dosage calculations and double-check requirements
   - Patient monitoring guidelines

#### **👨‍💼 Administrator Workflow**
1. **Upload Policy Documents:**
   - HIPAA compliance guides
   - Organizational policies
   - Quality assurance standards
   - Regulatory requirements

2. **Policy & Compliance Questions:**
   - *"What are our data retention requirements?"*
   - *"Show me the incident reporting procedure"*
   - *"What's required for Joint Commission compliance?"*

#### **🔒 Security Best Practices**

**🔑 API Key Management:**
```bash
# Store API keys securely (never in code)
export ***************"your-key-here"
export GALILEO_API_KEY="your-galileo-key"

# Use environment-specific keys
# Development: test keys with limited permissions
# Production: full keys with monitoring
```

**🏥 Department Access Control:**
```python
# Example: Only cardiology staff can access cardiology documents
# This is handled automatically by the Oso authorization system

# In authorization.polar:
allow(user: User, "read", document: Document) if
    user.department = document.department;
```

**📊 Audit & Monitoring:**
- All document access is logged with user, timestamp, and document
- AI queries are tracked for compliance and quality review
- Galileo provides AI performance monitoring and cost tracking
- Failed authorization attempts are logged for security review

#

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
# Install all dependencies (respects uv.lock for consistency)
uv sync

# Install development tools
uv sync --group dev

# Start development services
./run_all.sh

# Run database migrations
docker-compose run --rm migrate

# Seed demo data
uv run python -m common.seed_data

# Run tests (when available)
uv run pytest

# Format code
uv run ruff format .

# Lint code
uv run ruff check .

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
docker-compose -f docker-compose.prod.yml up -d

# Or build individual services
docker build -f Dockerfile.auth -t auth-service .
docker build -f Dockerfile.patient -t patient-service .
docker build -f Dockerfile.rag -t rag-service .
```

### Backup & Recovery

```bash
# Database backup
docker exec healthcare-support-portal-postgres-1 \
  pg_dump -U postgres healthcare > backup_$(date +%Y%m%d).sql

# Document backup (export all documents)
uv run python -c "
import json
from datetime import date
from packages.common.db import SessionLocal
from packages.common.models import Document

with SessionLocal() as db:
    docs = db.query(Document).all()
    backup = [{'title': d.title, 'content': d.content, 'department': d.department} for d in docs]
    with open(f'documents_backup_{date.today().isoformat()}.json', 'w') as f:
        json.dump(backup, f, indent=2)
print('Documents backed up successfully')
"

# Restore database
docker exec -i healthcare-support-portal-postgres-1 \
  psql -U postgres healthcare < backup_20241201.sql

# Monitor system performance
docker stats --no-stream
uv run python -c "from packages.rag.src.rag_service.main import app; print('RAG service health check passed')"
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

**Welcome to the future of intelligent knowledge management!** 🏥✨

