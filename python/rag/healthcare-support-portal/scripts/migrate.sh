#!/bin/bash
# scripts/migrate.sh - Run database migrations with retry logic and health checks

set -e  # Exit on error

echo "🔄 Healthcare Support Portal - Database Migration"
echo "================================================="

# Get database URL from environment or use default
DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare}"

# Extract connection details for psql
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\).*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\).*/\1/p')

echo "📊 Database Configuration:"
echo "   Host: $DB_HOST"
echo "   Port: $DB_PORT"
echo "   Database: $DB_NAME"
echo ""

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
MAX_WAIT=30
for i in $(seq 1 $MAX_WAIT); do
  if PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ Database is ready!"
    break
  fi
  
  if [ $i -eq $MAX_WAIT ]; then
    echo "❌ Database is not available after ${MAX_WAIT} seconds"
    exit 1
  fi
  
  echo "   Waiting for database... (attempt $i/$MAX_WAIT)"
  sleep 1
done

# Change to common package directory where alembic.ini is located
cd /app/packages/common || cd packages/common

echo ""
echo "🔍 Checking current migration status..."
# Use uv from PATH (works in both Docker and local environments)
UV_CMD="uv"
if [ -f "/opt/homebrew/bin/uv" ]; then
    UV_CMD="/opt/homebrew/bin/uv"
fi

if $UV_CMD run alembic current 2>/dev/null; then
  echo "   Current migration retrieved successfully"
else
  echo "   No migrations found (fresh database)"
fi

# Run migrations with retry logic
echo ""
echo "🚀 Running database migrations..."
MAX_RETRIES=3

for i in $(seq 1 $MAX_RETRIES); do
  echo "   Attempt $i of $MAX_RETRIES..."
  
  if $UV_CMD run alembic upgrade head; then
    echo ""
    echo "✅ Migrations completed successfully!"
    
    # Show current migration after success
    echo ""
    echo "📋 Current migration status:"
    $UV_CMD run alembic current
    
    exit 0
  fi
  
  if [ $i -eq $MAX_RETRIES ]; then
    echo ""
    echo "❌ Migration failed after $MAX_RETRIES attempts"
    echo "   Please check the error messages above and ensure:"
    echo "   1. The database is accessible"
    echo "   2. The database user has proper permissions"
    echo "   3. The migration files are valid"
    exit 1
  fi
  
  echo "⚠️  Migration attempt $i failed, retrying in 2 seconds..."
  sleep 2
done