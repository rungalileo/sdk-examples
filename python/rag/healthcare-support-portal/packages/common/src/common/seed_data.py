#!/usr/bin/env python3
"""
Database seeding script for Healthcare Support Portal
Creates demo users, patients, and documents for development and demonstration.

This script is idempotent - safe to run multiple times without creating duplicates.
"""

import sys
import time

import requests
from sqlalchemy.orm import Session

from .auth import get_password_hash
from .db import SessionLocal
from .models import Document, Patient, User
from .oso_sync import (
    sync_admin_global_access,
    sync_patient_access,
)

# Service URLs - update these based on your environment
AUTH_SERVICE_URL = "http://localhost:8001"
PATIENT_SERVICE_URL = "http://localhost:8002"
RAG_SERVICE_URL = "http://localhost:8003"


def wait_for_services():
    """Wait for services to be available before seeding"""
    services = [
        (AUTH_SERVICE_URL, "Auth Service"),
        (PATIENT_SERVICE_URL, "Patient Service"),
        (RAG_SERVICE_URL, "RAG Service"),
    ]

    for url, name in services:
        for attempt in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ {name} is ready")
                    break
            except requests.RequestException:
                if attempt < 29:
                    print(f"⏳ Waiting for {name}... (attempt {attempt + 1})")
                    time.sleep(1)
                else:
                    print(f"❌ {name} is not available after 30 seconds")
                    return False
    return True


def get_admin_token(db: Session) -> str:
    """Get admin token for API calls"""
    # First, create admin user directly in database (bootstrap)
    admin_user = db.query(User).filter(User.username == "admin_wilson").first()
    if not admin_user:
        # Create admin user directly for bootstrapping
        hashed_password = get_password_hash("secure_password")
        admin_user = User(
            username="admin_wilson",
            email="jennifer.wilson@hospital.com",
            hashed_password=hashed_password,
            role="admin",
            department="administration",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        # Sync OSO facts for admin user
        try:
            sync_admin_global_access(admin_user)
            print(f"🔐 Created bootstrap admin user: {admin_user.username}")
        except Exception as e:
            print(f"⚠️  Failed to sync OSO facts for bootstrap admin: {e}")

    # Get auth token
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/api/v1/auth/login",
            data={"username": "admin_wilson", "password": "secure_password"},
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    except Exception as e:
        print(f"❌ Failed to get admin token: {e}")
        return None


def seed_users(db: Session, admin_token: str) -> dict[str, User]:
    """Create demo users using API calls."""
    created_users = {}

    # Admin user is already created during bootstrap, just get it
    admin_user = db.query(User).filter(User.username == "admin_wilson").first()
    if admin_user:
        created_users["admin_wilson"] = admin_user
        print("✅ Using bootstrap admin user: admin_wilson")

    demo_users = [
        {
            "username": "dr_smith",
            "email": "sarah.smith@hospital.com",
            "password": "secure_password",
            "role": "doctor",
            "department": "cardiology",
            "full_name": "Dr. Sarah Smith",
        },
        {
            "username": "nurse_johnson",
            "email": "michael.johnson@hospital.com",
            "password": "secure_password",
            "role": "nurse",
            "department": "emergency",
            "full_name": "Nurse Michael Johnson",
        },
    ]

    headers = {"Authorization": f"Bearer {admin_token}"}

    for user_data in demo_users:
        # Check if user already exists
        existing_user = (
            db.query(User).filter(User.username == user_data["username"]).first()
        )
        if existing_user:
            print(f"✅ User '{user_data['username']}' already exists, skipping")
            created_users[user_data["username"]] = existing_user
            continue

        # Create user via API
        try:
            response = requests.post(
                f"{AUTH_SERVICE_URL}/api/v1/users/",
                json={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password": user_data["password"],
                    "role": user_data["role"],
                    "department": user_data["department"],
                },
                headers=headers,
            )

            if response.status_code == 200:
                user_response = response.json()
                # Get user from database
                new_user = db.query(User).filter(User.id == user_response["id"]).first()
                created_users[user_data["username"]] = new_user
                print(
                    f"✅ Created user via API: {user_data['full_name']} ({user_data['username']})"
                )
            else:
                print(
                    f"⚠️  Failed to create user {user_data['username']}: {response.text}"
                )

        except Exception as e:
            print(f"⚠️  Error creating user {user_data['username']}: {e}")

    return created_users


def seed_patients(
    db: Session, users: dict[str, User], admin_token: str
) -> list[Patient]:
    """Create demo patients via API if they don't exist."""
    created_patients = []

    # Get the doctor user
    doctor = users.get("dr_smith")
    if not doctor:
        print("⚠️  Doctor user not found, skipping patient creation")
        return created_patients

    demo_patients = [
        {
            "name": "John Anderson",
            "medical_record_number": "MRN-2024-001",
            "department": "cardiology",
            "date_of_birth": "1965-03-15",
            "assigned_doctor_id": doctor.id,
        },
        {
            "name": "Maria Rodriguez",
            "medical_record_number": "MRN-2024-002",
            "department": "cardiology",
            "date_of_birth": "1978-08-22",
            "assigned_doctor_id": doctor.id,
        },
        {
            "name": "Robert Chen",
            "medical_record_number": "MRN-2024-003",
            "department": "cardiology",
            "date_of_birth": "1952-11-08",
            "assigned_doctor_id": doctor.id,
        },
    ]

    headers = {"Authorization": f"Bearer {admin_token}"}

    for patient_data in demo_patients:
        # Check if patient already exists
        existing_patient = (
            db.query(Patient)
            .filter(
                Patient.medical_record_number == patient_data["medical_record_number"]
            )
            .first()
        )
        if existing_patient:
            print(
                f"✅ Patient '{patient_data['name']}' (MRN: {patient_data['medical_record_number']}) already exists, skipping"
            )
            created_patients.append(existing_patient)

            # Sync OSO facts for existing patients (in case they weren't synced before)
            try:
                sync_patient_access(existing_patient)
                print(
                    f"🔐 Synced access facts for existing patient {patient_data['name']}"
                )
            except Exception as e:
                print(
                    f"⚠️  Failed to sync OSO facts for existing patient {patient_data['name']}: {e}"
                )
            continue

        # Create patient via Patient Service API
        try:
            response = requests.post(
                f"{PATIENT_SERVICE_URL}/api/v1/patients/",
                json={
                    "name": patient_data["name"],
                    "medical_record_number": patient_data["medical_record_number"],
                    "department": patient_data["department"],
                    "date_of_birth": patient_data["date_of_birth"],
                    "assigned_doctor_id": patient_data["assigned_doctor_id"],
                },
                headers=headers,
            )

            if response.status_code == 200:
                patient_response = response.json()
                # Get patient from database
                new_patient = (
                    db.query(Patient)
                    .filter(Patient.id == patient_response["id"])
                    .first()
                )
                created_patients.append(new_patient)
                print(
                    f"✅ Created patient via API (with OSO facts): {patient_data['name']} (MRN: {patient_data['medical_record_number']})"
                )
            else:
                print(
                    f"⚠️  Failed to create patient {patient_data['name']}: {response.text}"
                )

        except Exception as e:
            print(f"⚠️  Error creating patient {patient_data['name']}: {e}")

    return created_patients


def seed_documents(
    db: Session, users: dict[str, User], patients: list[Patient], admin_token: str
) -> list[Document]:
    """Create demo documents if they don't exist."""
    created_documents = []

    # Get the doctor user
    doctor = users.get("dr_smith")
    if not doctor:
        print("⚠️  Doctor user not found, skipping document creation")
        return created_documents

    demo_documents = [
        {
            "title": "Cardiology Department Protocols",
            "content": """# Cardiology Department Standard Operating Procedures

## Patient Assessment Protocols
1. Initial cardiac risk assessment for all new patients
2. ECG interpretation guidelines and red flags
3. Chest pain evaluation protocols
4. Heart failure management guidelines

## Diagnostic Procedures
- Echocardiogram ordering criteria
- Stress test indications and contraindications
- Cardiac catheterization preparation protocols
- Post-procedure monitoring requirements

## Medication Management
- ACE inhibitor dosing and monitoring
- Beta-blocker titration protocols
- Anticoagulation management
- Drug interaction guidelines

## Emergency Procedures
- Code Blue response protocols
- Cardiac arrest management
- Acute MI treatment pathways
- Arrhythmia management protocols

Last updated: January 2024""",
            "document_type": "protocol",
            "department": "cardiology",
            "is_sensitive": False,
        },
        {
            "title": "Hypertension Management Guidelines",
            "content": """# Hypertension Management Guidelines

## Classification
- Normal: <120/80 mmHg
- Elevated: 120-129/<80 mmHg  
- Stage 1: 130-139/80-89 mmHg
- Stage 2: ≥140/≥90 mmHg
- Crisis: >180/>120 mmHg

## Initial Assessment
1. Confirm diagnosis with multiple readings
2. Assess for secondary causes
3. Evaluate cardiovascular risk factors
4. Screen for target organ damage

## Treatment Approach
### Lifestyle Modifications
- DASH diet implementation
- Sodium restriction (<2.3g/day)
- Weight management (BMI <25)
- Regular aerobic exercise (150 min/week)
- Alcohol moderation
- Smoking cessation

### Pharmacological Treatment
First-line agents:
- ACE inhibitors or ARBs
- Calcium channel blockers
- Thiazide diuretics

## Monitoring
- BP checks every 2-4 weeks during titration
- Annual lab work (creatinine, potassium)
- Yearly cardiovascular risk assessment

Target: <130/80 mmHg for most patients""",
            "document_type": "guideline",
            "department": "cardiology",
            "is_sensitive": False,
        },
        {
            "title": "Heart Failure Patient Education",
            "content": """# Heart Failure: Patient Education Guide

## What is Heart Failure?
Heart failure occurs when your heart cannot pump blood effectively to meet your body's needs. This doesn't mean your heart has stopped working, but rather that it needs support to work better.

## Common Symptoms
- Shortness of breath (especially when lying down)
- Fatigue and weakness
- Swelling in legs, ankles, or feet
- Rapid or irregular heartbeat
- Persistent cough or wheezing
- Weight gain from fluid retention

## Daily Management
### Medications
- Take all medications as prescribed
- Never skip doses
- Know your medications and their purposes
- Report side effects to your healthcare team

### Diet and Fluid Management
- Limit sodium intake (less than 2 grams daily)
- Monitor fluid intake as directed
- Weigh yourself daily at the same time
- Call if weight increases by 2-3 pounds in one day

### Activity Guidelines
- Stay active within your limits
- Pace yourself and rest when needed
- Avoid sudden increases in activity
- Participate in cardiac rehabilitation if recommended

## When to Call Your Doctor
- Weight gain of 2-3 pounds in one day
- Increased shortness of breath
- New or worsening swelling
- Chest pain or discomfort
- Dizziness or fainting
- Any concerns about your condition

Remember: You are an important part of your healthcare team!""",
            "document_type": "education",
            "department": "cardiology",
            "is_sensitive": False,
        },
    ]

    headers = {"Authorization": f"Bearer {admin_token}"}

    for doc_data in demo_documents:
        # Check if document already exists (by title)
        existing_doc = (
            db.query(Document).filter(Document.title == doc_data["title"]).first()
        )
        if existing_doc:
            print(f"✅ Document '{doc_data['title']}' already exists, skipping")
            created_documents.append(existing_doc)
            continue

        # Create document via RAG service API (this will automatically generate embeddings!)
        try:
            response = requests.post(
                f"{RAG_SERVICE_URL}/api/v1/documents/",
                json={
                    "title": doc_data["title"],
                    "content": doc_data["content"],
                    "document_type": doc_data["document_type"],
                    "department": doc_data["department"],
                    "is_sensitive": doc_data["is_sensitive"],
                },
                headers=headers,
            )

            if response.status_code == 200:
                doc_response = response.json()
                # Get document from database
                new_document = (
                    db.query(Document).filter(Document.id == doc_response["id"]).first()
                )
                created_documents.append(new_document)
                print(
                    f"✅ Created document via RAG API (with embeddings): {doc_data['title']}"
                )
            else:
                print(
                    f"⚠️  Failed to create document {doc_data['title']}: {response.text}"
                )

        except Exception as e:
            print(f"⚠️  Error creating document {doc_data['title']}: {e}")

    # Create patient-specific documents
    if patients:
        patient_docs = [
            {
                "title": f"Medical History - {patients[0].name}",
                "content": f"""# Medical History for {patients[0].name}
MRN: {patients[0].medical_record_number}

## Chief Complaint
Routine cardiac follow-up for hypertension and coronary artery disease.

## History of Present Illness
67-year-old male with history of hypertension, hyperlipidemia, and prior MI in 2020. Currently stable on optimal medical therapy. Reports good exercise tolerance and no chest pain.

## Past Medical History
- Hypertension (2015)
- Hyperlipidemia (2016)
- ST-elevation myocardial infarction (2020)
- Percutaneous coronary intervention with drug-eluting stent to LAD (2020)

## Current Medications
- Metoprolol succinate 50mg daily
- Lisinopril 10mg daily
- Atorvastatin 80mg daily
- Aspirin 81mg daily
- Clopidogrel 75mg daily

## Allergies
No known drug allergies

## Social History
Former smoker (quit 2020), occasional alcohol use, married, retired electrician.

## Assessment and Plan
Stable coronary artery disease. Continue current medications. Next follow-up in 6 months with stress test if symptoms develop.""",
                "document_type": "medical_record",
                "patient_id": patients[0].id,
                "is_sensitive": True,
            }
        ]

        for doc_data in patient_docs:
            # Check if patient document already exists
            existing_doc = (
                db.query(Document)
                .filter(
                    Document.title == doc_data["title"],
                    Document.patient_id == doc_data["patient_id"],
                )
                .first()
            )
            if existing_doc:
                print(
                    f"✅ Patient document '{doc_data['title']}' already exists, skipping"
                )
                created_documents.append(existing_doc)
                continue

            # Create patient document via RAG service API (with embeddings!)
            try:
                response = requests.post(
                    f"{RAG_SERVICE_URL}/api/v1/documents/",
                    json={
                        "title": doc_data["title"],
                        "content": doc_data["content"],
                        "document_type": doc_data["document_type"],
                        "department": "cardiology",
                        "patient_id": doc_data["patient_id"],
                        "is_sensitive": doc_data["is_sensitive"],
                    },
                    headers=headers,
                )

                if response.status_code == 200:
                    doc_response = response.json()
                    # Get document from database
                    new_document = (
                        db.query(Document)
                        .filter(Document.id == doc_response["id"])
                        .first()
                    )
                    created_documents.append(new_document)
                    print(
                        f"✅ Created patient document via RAG API (with embeddings): {doc_data['title']}"
                    )
                else:
                    print(
                        f"⚠️  Failed to create patient document {doc_data['title']}: {response.text}"
                    )

            except Exception as e:
                print(f"⚠️  Error creating patient document {doc_data['title']}: {e}")

    return created_documents


def main() -> None:
    """Main seeding function."""
    print("🌱 Healthcare Support Portal - Database Seeding")
    print("=" * 50)

    try:
        # Note: Database migrations should be run before seeding
        print("📊 Database migrations should already be applied")
        print("   If not, run: docker-compose run migrate")

        # Create database session
        db = SessionLocal()

        try:
            # Wait for services to be available
            print("\n⏳ Waiting for services to be ready...")
            if not wait_for_services():
                print("❌ Services not available, exiting...")
                return

            # Get admin token for API calls
            print("\n🔑 Getting admin authentication token...")
            admin_token = get_admin_token(db)
            if not admin_token:
                print("❌ Could not get admin token, exiting...")
                return

            # Seed users via API
            print("\n👥 Seeding demo users via API...")
            users = seed_users(db, admin_token)

            # Seed patients via Patient API
            print("\n🏥 Seeding demo patients via API...")
            patients = seed_patients(db, users, admin_token)

            # Seed documents via RAG API (this will generate embeddings!)
            print("\n📄 Seeding demo documents via RAG API...")
            documents = seed_documents(db, users, patients, admin_token)

            print("\n" + "=" * 50)
            print("🎉 Seeding completed successfully!")
            print(f"   Users created/verified: {len(users)}")
            print(f"   Patients created/verified: {len(patients)}")
            print(f"   Documents created/verified: {len(documents)}")
            print(
                "   📊 Documents created via RAG API include vector embeddings for chat!"
            )
            print("\n🔐 Demo Login Credentials:")
            print("   Doctor:  dr_smith / secure_password")
            print("   Nurse:   nurse_johnson / secure_password")
            print("   Admin:   admin_wilson / secure_password")
            print("\n🌐 Access the application at: http://localhost:3000")
            print("💬 Try the chat feature - it should now find relevant documents!")

        finally:
            db.close()

    except Exception as e:
        print(f"\n❌ Seeding failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
