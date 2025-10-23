from datetime import datetime

from pydantic import BaseModel, ConfigDict


# User schemas
class UserBase(BaseModel):
    username: str
    email: str
    role: str
    department: str | None = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


# Patient schemas
class PatientBase(BaseModel):
    name: str
    medical_record_number: str
    department: str | None = None


class PatientCreate(PatientBase):
    date_of_birth: str | None = None  # ISO date string format YYYY-MM-DD
    assigned_doctor_id: int | None = None


class PatientResponse(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_of_birth: datetime | None = None
    assigned_doctor_id: int | None
    is_active: bool
    created_at: datetime


# Document schemas
class DocumentBase(BaseModel):
    title: str
    content: str
    document_type: str
    department: str | None = None
    is_sensitive: bool = False


class DocumentCreate(DocumentBase):
    patient_id: int | None = None


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int | None
    created_by_id: int
    created_at: datetime


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
