#!/usr/bin/env python3
"""
Configuration Test Script for Healthcare RAG Service

This script tests that all required environment variables and API keys
are properly configured for the RAG service.

Usage:
    uv run python test_config.py
"""

import os
import sys
from typing import Dict, Any

from dotenv import load_dotenv

load_dotenv()


def test_environment_variables() -> Dict[str, Any]:
    """Test that all required environment variables are set."""
    results = {}

    # Required variables
    required_vars = {
        "DATABASE_URL": "PostgreSQL database connection string",
        "SECRET_KEY": "JWT signing key",
        "OPENAI_API_KEY": "OpenAI API key for embeddings and chat",
    }

    # Optional variables with defaults
    optional_vars = {
        "DEBUG": "Debug mode (default: false)",
        "EMBEDDING_MODEL": "OpenAI embedding model (default: text-embedding-3-small)",
        "CHAT_MODEL": "OpenAI chat model (default: gpt-4o-mini)",
        "GALILEO_API_KEY": "Galileo API key for observability",
        "GALILEO_PROJECT_NAME": "Galileo project name (default: healthcare-rag)",
        "GALILEO_ENVIRONMENT": "Galileo environment tag (default: development)",
        "CHUNK_SIZE": "Document chunk size (default: 1000)",
        "SIMILARITY_THRESHOLD": "Vector search threshold (default: 0.7)",
    }

    print("🔍 Testing Environment Variables...")
    print("=" * 50)

    # Test required variables
    all_required_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == "OPENAI_API_KEY":
                # Don't expose the full key
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "[HIDDEN]"
            else:
                display_value = f"{value[:20]}..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
            results[var] = {"status": "OK", "value": value}
        else:
            print(f"❌ {var}: NOT SET ({description})")
            results[var] = {"status": "MISSING", "value": None}
            all_required_present = False

    print()

    # Test optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if "API_KEY" in var:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "[HIDDEN]"
            else:
                display_value = value
            print(f"🟡 {var}: {display_value}")
            results[var] = {"status": "SET", "value": value}
        else:
            print(f"⚪ {var}: Not set ({description})")
            results[var] = {"status": "DEFAULT", "value": None}

    results["all_required_present"] = all_required_present
    return results


def test_openai_connection() -> bool:
    """Test OpenAI API connection."""
    try:
        import openai
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OpenAI API key not found")
            return False

        if not api_key.startswith("sk-"):
            print(f"❌ OpenAI API key format invalid (should start with 'sk-'): {api_key[:10]}...")
            return False

        print("⚙️ Testing OpenAI API connection...")
        client = OpenAI(api_key=api_key)

        # Test with a simple API call
        models = client.models.list()
        print(f"✅ OpenAI API connection successful ({len(models.data)} models available)")
        return True

    except ImportError:
        print("❌ OpenAI package not installed. Run: uv add openai")
        return False
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {str(e)}")
        return False


def test_database_connection() -> bool:
    """Test database connection."""
    try:
        from sqlalchemy import create_engine, text

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL not found")
            return False

        print("⚙️ Testing database connection...")
        engine = create_engine(db_url)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful")
            print(f"   PostgreSQL version: {version.split(',')[0]}")

            # Check for pgvector extension
            result = conn.execute(text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"))
            has_vector = result.fetchone()[0]
            if has_vector:
                print(f"✅ pgvector extension is installed")
            else:
                print(f"⚠️ pgvector extension not found (required for embeddings)")

        return True

    except ImportError as e:
        print(f"❌ Database packages not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False


def test_galileo_connection() -> bool:
    """Test Galileo API connection."""
    try:
        api_key = os.getenv("GALILEO_API_KEY")
        if not api_key or api_key == "your-galileo-api-key-here":
            print("⚠️ Galileo API key not configured (using default placeholder)")
            print("   Get your API key from: https://app.galileo.ai/sign-up")
            return True  # Don't fail the config test, just warn

        # For now, just check that the key exists
        # A full test would require the galileo package and network call
        print(f"✅ Galileo API key configured ({api_key[:8]}...)")

        project = os.getenv("GALILEO_PROJECT_NAME", "healthcare-rag")
        environment = os.getenv("GALILEO_ENVIRONMENT", "development")
        print(f"   Project: {project}")
        print(f"   Environment: {environment}")

        return True

    except Exception as e:
        print(f"❌ Galileo configuration error: {str(e)}")
        return False


def main():
    """Run all configuration tests."""
    print("🏥 Healthcare RAG Configuration Test")
    print("=" * 50)
    print()

    # Test environment variables
    env_results = test_environment_variables()
    env_ok = env_results["all_required_present"]
    print()

    # Test connections
    openai_ok = test_openai_connection()
    print()

    db_ok = test_database_connection()
    print()

    galileo_ok = test_galileo_connection()
    print()

    # Summary
    print("=" * 50)
    print("📊 Configuration Test Summary:")
    print(f"   Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"   OpenAI Connection: {'✅ PASS' if openai_ok else '❌ FAIL'}")
    print(f"   Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"   Galileo Configuration: {'✅ PASS' if galileo_ok else '❌ FAIL'}")
    print()

    if all([env_ok, openai_ok, db_ok, galileo_ok]):
        print("🎉 All tests passed! RAG service is ready to run.")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Please fix the issues above before running the RAG service.")
        print()
        print("🔧 Quick fixes:")
        if not env_ok:
            print("   - Copy .env.example to .env and fill in your API keys")
        if not openai_ok:
            print("   - Get your OpenAI API key from https://platform.openai.com/api-keys")
        if not db_ok:
            print("   - Make sure PostgreSQL is running with: docker-compose up -d db")
        if not galileo_ok:
            print("   - Set GALILEO_ENABLED=false or add your Galileo API key")
        sys.exit(1)


if __name__ == "__main__":
    main()
