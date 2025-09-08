"""
Migration verification utilities for services.
Ensures database migrations are up-to-date before service startup.
"""

import os
import sys
from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine


def get_alembic_config() -> Config:
    """Get Alembic configuration from the common package."""
    # Find the alembic.ini file in the common package
    common_dir = Path(__file__).parent.parent.parent  # Go up to packages/common
    alembic_ini = common_dir / "alembic.ini"

    if not alembic_ini.exists():
        raise FileNotFoundError(
            f"alembic.ini not found at {alembic_ini}. " "Please ensure Alembic is properly initialized."
        )

    config = Config(str(alembic_ini))

    # Set the script location to absolute path
    script_location = common_dir / "alembic"
    config.set_main_option("script_location", str(script_location))

    return config


def verify_migrations_current(database_url: str = None) -> bool:
    """
    Verify that database migrations are up to date.

    Args:
        database_url: Database connection URL. If None, uses DATABASE_URL env var.

    Returns:
        True if migrations are current, False otherwise.
    """
    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare",
        )

    try:
        # Create engine and get current database revision
        engine = create_engine(database_url)

        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()

        # Get the head revision from Alembic scripts
        config = get_alembic_config()
        script = ScriptDirectory.from_config(config)
        head_rev = script.get_current_head()

        if current_rev != head_rev:
            print("❌ Database migrations are out of date!")
            print(f"   Current revision: {current_rev or 'None (no migrations applied)'}")
            print(f"   Head revision: {head_rev}")
            print("")
            print("   To fix this, run one of the following:")
            print("   1. Docker Compose: docker-compose run migrate")
            print("   2. Manual: cd packages/common && uv run alembic upgrade head")
            print("")
            return False

        print(f"✅ Database migrations are up to date (revision: {current_rev})")
        return True

    except Exception as e:
        print(f"❌ Error checking migration status: {e}")
        print("   This might indicate:")
        print("   1. Database is not accessible")
        print("   2. Migrations have not been initialized")
        print("   3. Database connection issues")
        return False


def require_migrations_current(database_url: str = None) -> None:
    """
    Require migrations to be current, exit if not.

    This should be called at service startup to ensure
    the database schema is up to date.

    Args:
        database_url: Database connection URL. If None, uses DATABASE_URL env var.
    """
    if not verify_migrations_current(database_url):
        print("🛑 Service startup aborted due to outdated migrations.")
        print("   Please run migrations before starting the service.")
        sys.exit(1)
