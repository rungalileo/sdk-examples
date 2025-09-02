#!/bin/bash
# setup.sh - Initial setup for Healthcare Support Portal

echo "🏥 Healthcare Support Portal - Initial Setup"
echo "============================================="

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/postgres

# Set up Python environment first
echo "🐍 Setting up Python environment..."
# Use uv from PATH (works in both Docker and local environments)
UV_CMD="uv"
if [ -f "/opt/homebrew/bin/uv" ]; then
    UV_CMD="/opt/homebrew/bin/uv"
fi

$UV_CMD sync

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

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x run_all.sh
chmod +x stop_all.sh
chmod +x packages/auth/run.sh
chmod +x packages/patient/run.sh
chmod +x packages/rag/run.sh
chmod +x frontend/run.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit packages/rag/.env and add your OpenAI API key"
echo "2. Start the database: docker-compose up -d"
echo "3. Run database migrations: docker-compose run migrate"
echo "4. Install frontend dependencies: cd frontend && npm install"  
echo "5. Seed demo data: $UV_CMD run python -m common.seed_data"
echo "6. Start all services: ./run_all.sh"
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
