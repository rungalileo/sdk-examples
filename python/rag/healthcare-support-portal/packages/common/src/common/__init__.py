"""
Common package for Healthcare Support Portal
Shared models, database utilities, and policies
"""

from .auth import create_access_token, get_current_user, verify_password
from .db import SessionLocal, engine, get_db
from .models import Base, Document, Embedding, Patient, User

__all__ = [
    "Base",
    "User",
    "Patient",
    "Document",
    "Embedding",
    "get_db",
    "engine",
    "SessionLocal",
    "get_current_user",
    "create_access_token",
    "verify_password",
]
