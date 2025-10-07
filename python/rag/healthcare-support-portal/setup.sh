#!/bin/bash
# setup.sh - Cross-platform initial setup for Healthcare Support Portal
# Compatible with macOS, Linux, and Windows (via Git Bash or WSL)

# Exit on any error
set -e

# Detect operating system
OS="Unknown"
case "$(uname -s)" in
    Darwin*)    OS="macOS";;
    Linux*)     OS="Linux";;
    CYGWIN*)    OS="Windows";;
    MINGW*)     OS="Windows";;
    MSYS*)      OS="Windows";;
esac

echo "🏥 Healthcare Support Portal - Initial Setup ($OS)"
echo "================================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare version numbers
version_ge() {
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"
}

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/postgres

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
if ! version_ge "$PYTHON_VERSION" "3.11.0"; then
    echo "❌ Python $PYTHON_VERSION found, but 3.11+ is required."
    exit 1
fi
echo "✅ Python $PYTHON_VERSION is compatible"

# Check uv
UV_CMD="uv"
if [ -f "/opt/homebrew/bin/uv" ]; then
    UV_CMD="/opt/homebrew/bin/uv"
fi

if ! command_exists "$UV_CMD"; then
    echo "❌ uv package manager not found. Installing..."
    if command_exists curl; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        UV_CMD="uv"
    else
        echo "❌ curl not found. Please install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
fi
echo "✅ uv package manager found"

# Set up Python environment
echo "🐍 Setting up Python environment..."
if ! $UV_CMD sync; then
    echo "❌ Failed to sync Python dependencies with uv"
    exit 1
fi
echo "✅ Python dependencies synced"

# Copy example .env files
echo "📋 Setting up environment files..."
for service in auth patient rag; do
    if [ ! -f "packages/$service/.env" ]; then
        if [ -f "packages/$service/.env.example" ]; then
            cp "packages/$service/.env.example" "packages/$service/.env"
            echo "✅ Created packages/$service/.env from example"
        fi
    else
        echo "⚠️  packages/$service/.env already exists, skipping"
    fi
done

# Generate a secure SECRET_KEY
echo "🔑 Generating secure SECRET_KEY..."
SECRET_KEY=$($UV_CMD run python -c "import secrets; print(secrets.token_urlsafe(32))")

# Update .env files with the generated SECRET_KEY
echo "🔄 Updating .env files with generated SECRET_KEY..."
for service in auth patient rag; do
    if [ -f "packages/$service/.env" ]; then
        sed -i.bak "s/SECRET_KEY=change-me-in-production/SECRET_KEY=$SECRET_KEY/" "packages/$service/.env"
        rm "packages/$service/.env.bak" 2>/dev/null || true
        echo "✅ Updated SECRET_KEY in packages/$service/.env"
    fi
done

# Make scripts executable (Unix/Linux/macOS only)
if [ "$OS" != "Windows" ]; then
    echo "🔧 Making scripts executable..."
    chmod +x run_all.sh
    chmod +x stop_all.sh
    chmod +x packages/auth/run.sh
    chmod +x packages/patient/run.sh
    chmod +x packages/rag/run.sh
    chmod +x frontend/run.sh
else
    echo "🔧 Scripts ready (Windows detected - no chmod needed)..."
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."

# Check Node.js
if ! command_exists node; then
    echo "❌ Node.js not found. Please install Node.js 20.19.0+ from https://nodejs.org/"
    echo "   After installation, run: cd frontend && npm install"
    echo "⚠️  Continuing with backend setup only..."
else
    NODE_VERSION=$(node --version | sed 's/v//')
    if version_ge "$NODE_VERSION" "20.19.0"; then
        echo "✅ Node.js $NODE_VERSION is compatible"
        
        # Check npm
        if ! command_exists npm; then
            echo "❌ npm not found. Please reinstall Node.js or install npm separately."
            exit 1
        fi
        
        # Install frontend dependencies
        if [ -f "frontend/package.json" ]; then
            echo "📦 Installing frontend packages with npm..."
            cd frontend
            if npm install; then
                echo "✅ Frontend dependencies installed successfully"
            else
                echo "❌ Failed to install frontend dependencies"
                cd ..
                exit 1
            fi
            cd ..
        else
            echo "❌ frontend/package.json not found"
            exit 1
        fi
    else
        echo "❌ Node.js $NODE_VERSION found, but 20.19.0+ is required."
        echo "   Please upgrade Node.js and run: cd frontend && npm install"
        echo "⚠️  Continuing with backend setup only..."
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. 🔑 Add your OpenAI API key to packages/rag/.env (REQUIRED)"
echo "   - Get your key at: https://platform.openai.com/api-keys"
echo "   - Replace '***************************' with your actual key"

if [ "$OS" = "Windows" ]; then
    echo "2. 🚀 Start all services:"
    echo "   - Using Docker: docker-compose up -d"
    echo "   - Or manually: Start each service in separate terminals"
    echo "   - Windows users: Use 'bash run_all.sh' or run services individually"
else
    echo "2. 🚀 Start all services: ./run_all.sh"
fi

echo "3. 🌱 Seed demo data: $UV_CMD run python -m common.seed_data"
echo "4. 🌐 Open http://localhost:3000 in your browser"
echo ""
echo "🔐 Demo Login Credentials (after seeding):"
echo "   Doctor:  dr_smith / secure_password"
echo "   Nurse:   nurse_johnson / secure_password"
echo "   Admin:   admin_wilson / secure_password"
echo ""
echo "📚 API Documentation will be available at:"
echo "   🔐 Auth Service:    http://localhost:8001/docs"
echo "   🏥 Patient Service: http://localhost:8002/docs"
echo "   🤖 RAG Service:     http://localhost:8003/docs"
