from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy_oso_cloud.oso import Resource

Base = declarative_base()


class User(Base, Resource):
    __tablename__ = "users"

    # OSO Cloud type identifier
    type = "User"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # doctor, nurse, admin
    department = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assigned_patients = relationship("Patient", back_populates="assigned_doctor")


class Patient(Base, Resource):
    __tablename__ = "patients"

    # OSO Cloud type identifier
    type = "Patient"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime)
    medical_record_number = Column(String(50), unique=True, index=True)
    department = Column(String(100))
    assigned_doctor_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assigned_doctor = relationship("User", back_populates="assigned_patients")
    documents = relationship("Document", back_populates="patient")


class Document(Base, Resource):
    __tablename__ = "documents"

    # OSO Cloud type identifier
    type = "Document"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String(50))  # medical_record, protocol, policy, etc.
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    department = Column(String(100))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    is_sensitive = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="documents")
    created_by = relationship("User")
    embeddings = relationship("Embedding", back_populates="document")


class Embedding(Base, Resource):
    __tablename__ = "embeddings"

    # OSO Cloud type identifier
    type = "Embedding"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    content_chunk = Column(Text, nullable=False)
    embedding_vector = Column(Vector(1536))  # OpenAI embedding dimension
    chunk_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="embeddings")
