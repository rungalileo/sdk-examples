# Common Package

This package contains shared components used across all microservices in the Healthcare Support Portal.

## Contents

- **Models** (`src/common/models.py`): SQLAlchemy database models for User, Patient, and Document entities
- **Database utilities** (`src/common/db.py`): Database connection, table creation, and pgvector extension management  
- **Schemas** (`src/common/schemas.py`): Pydantic schemas for API request/response validation

## Authorization

Authorization policies are managed centrally by the Oso Dev Server and loaded from the project root `authorization.polar` file. Individual services connect to the Oso Dev Server at runtime rather than loading policy files locally.

## Usage

All services import shared models and utilities from this package. The package is added to the Python path via each service's `run.sh` script.