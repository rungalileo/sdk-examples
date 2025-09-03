import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models to ensure they're registered with SQLAlchemy
# This is crucial for autogenerate to work
from common.models import Base

# Set the target metadata for autogenerate support
target_metadata = Base.metadata

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare")

# Override the ini file's sqlalchemy.url with environment variable
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Define naming conventions for constraints
# This ensures consistent naming across migrations
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

target_metadata.naming_convention = naming_convention


def include_object(object, name, type_, reflected, compare_to):
    """Filter out system objects from migrations"""
    # Skip any PostgreSQL internal schemas
    if type_ == "schema":
        return name not in ["information_schema", "pg_catalog", "pg_toast"]
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Enable pgvector extension if not exists
        # This needs to be done before migrations run
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
