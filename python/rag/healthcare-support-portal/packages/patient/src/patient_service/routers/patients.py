import sys
from pathlib import Path

# Add the common package to Python path
common_path = Path(__file__).parent.parent.parent.parent.parent / "common" / "src"
sys.path.insert(0, str(common_path))


from common.auth import get_current_user
from common.db import get_db
from common.models import Patient, User
from common.oso_sync import remove_patient_access, sync_patient_access
from common.schemas import PatientCreate, PatientResponse
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy_oso_cloud import authorized, get_oso

router = APIRouter()


@router.get("/", response_model=list[PatientResponse])
async def list_patients(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: str | None = Query(None),
):
    """
    List patients with Oso authorization filtering
    """
    # Use Oso Cloud to filter patients the current user can read
    query = db.query(Patient).options(authorized(current_user, "read", Patient))

    # Apply optional department filter
    if department:
        query = query.filter(Patient.department == department)

    # Apply pagination
    patients = query.offset(skip).limit(limit).all()

    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get specific patient with Oso authorization
    """
    oso = get_oso()

    # Get the patient
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Check if current user is authorized to read this patient
    if not oso.authorize(current_user, "read", patient):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this patient",
        )

    return patient


@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new patient
    """
    # Check if medical record number already exists
    existing_patient = (
        db.query(Patient).filter(Patient.medical_record_number == patient_data.medical_record_number).first()
    )

    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this medical record number already exists",
        )

    # Create new patient
    # Parse date_of_birth if provided
    date_of_birth = None
    if patient_data.date_of_birth:
        try:
            from datetime import datetime

            date_of_birth = datetime.fromisoformat(patient_data.date_of_birth)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_of_birth format. Use YYYY-MM-DD",
            )

    db_patient = Patient(
        name=patient_data.name,
        medical_record_number=patient_data.medical_record_number,
        department=patient_data.department,
        date_of_birth=date_of_birth,
        assigned_doctor_id=patient_data.assigned_doctor_id,
        is_active=True,
    )

    # Check if user is authorized to write/create patients
    # For creation, we'll check against a dummy patient object or use role-based logic
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create patients",
        )

    # If assigning to a doctor, ensure it's valid
    if patient_data.assigned_doctor_id:
        doctor = db.query(User).filter(User.id == patient_data.assigned_doctor_id, User.role == "doctor").first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid doctor assignment",
            )

    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)

    # Sync OSO facts for new patient
    try:
        sync_patient_access(db_patient)
    except Exception as e:
        print(f"Warning: Failed to sync OSO facts for new patient {db_patient.id}: {e}")

    return db_patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update patient with Oso authorization
    """
    oso = get_oso()

    # Get the patient
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Check if current user is authorized to write this patient
    if not oso.authorize(current_user, "write", patient):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this patient",
        )

    # Check for medical record number conflicts (if changed)
    if patient_update.medical_record_number != patient.medical_record_number:
        existing_patient = (
            db.query(Patient)
            .filter(
                Patient.medical_record_number == patient_update.medical_record_number,
                Patient.id != patient_id,
            )
            .first()
        )

        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this medical record number already exists",
            )

    # Parse date_of_birth if provided
    date_of_birth = None
    if patient_update.date_of_birth:
        try:
            from datetime import datetime

            date_of_birth = datetime.fromisoformat(patient_update.date_of_birth)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_of_birth format. Use YYYY-MM-DD",
            )

    # Track changes for OSO sync
    old_assigned_doctor_id = patient.assigned_doctor_id
    old_department = patient.department

    # Update patient fields
    patient.name = patient_update.name
    patient.medical_record_number = patient_update.medical_record_number
    patient.department = patient_update.department
    patient.date_of_birth = date_of_birth
    patient.assigned_doctor_id = patient_update.assigned_doctor_id

    db.commit()
    db.refresh(patient)

    # Sync OSO facts if assignments changed
    try:
        if old_assigned_doctor_id != patient.assigned_doctor_id or old_department != patient.department:
            # Resync all patient access facts
            sync_patient_access(patient)
    except Exception as e:
        print(f"Warning: Failed to sync OSO facts for updated patient {patient.id}: {e}")

    return patient


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Soft delete patient (set is_active to False)
    """
    oso = get_oso()

    # Get the patient
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Check if current user is authorized to write this patient
    if not oso.authorize(current_user, "write", patient):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this patient",
        )

    # Soft delete (set is_active to False)
    patient.is_active = False
    db.commit()

    # Remove OSO facts for deactivated patient
    try:
        remove_patient_access(patient.id)
    except Exception as e:
        print(f"Warning: Failed to remove OSO facts for deactivated patient {patient.id}: {e}")

    return {"message": "Patient deactivated successfully"}


@router.get("/search/by-department/{department}", response_model=list[PatientResponse])
async def search_patients_by_department(
    department: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Search patients by department with authorization
    """
    # Use Oso Cloud to filter patients the current user can read
    patients = (
        db.query(Patient)
        .options(*authorized(current_user, "read", Patient))
        .filter(Patient.department == department, Patient.is_active)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return patients
