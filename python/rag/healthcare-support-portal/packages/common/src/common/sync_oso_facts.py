#!/usr/bin/env python3
"""
Standalone script to synchronize OSO facts with database state.
This script initializes sqlalchemy-oso-cloud and syncs authorization facts.
"""

import os
import sys

import sqlalchemy_oso_cloud
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import Base, Document, Embedding, Patient, User
from .oso_sync import (
    sync_admin_global_access,
    sync_document_access,
    sync_embedding_access,
    sync_patient_access,
)


def initialize_oso() -> None:
    """Initialize SQLAlchemy OSO Cloud connection."""
    # OSO configuration - same as in the services
    oso_url = os.getenv("OSO_URL", "http://localhost:8080")
    oso_auth = os.getenv("OSO_AUTH", "e_0123456789_12345_osotesttoken01xiIn")

    # Initialize SQLAlchemy Oso Cloud with registry and server settings
    sqlalchemy_oso_cloud.init(Base.registry, url=oso_url, api_key=oso_auth)

    print(f"✅ Initialized OSO Cloud connection: {oso_url}")


def sync_all_facts() -> None:
    """Synchronize all authorization facts with OSO Cloud."""
    db: Session = SessionLocal()

    try:
        print("🔐 Starting comprehensive OSO fact synchronization...")

        # Sync admin users first
        print("\n👑 Syncing admin user facts...")
        admin_users = db.query(User).filter(User.role == "admin", User.is_active).all()
        for admin in admin_users:
            try:
                sync_admin_global_access(admin)
                print(f"✅ Synced global admin access for {admin.username}")
            except Exception as e:
                print(f"❌ Failed to sync admin access for {admin.username}: {e}")

        # Sync all patients
        print("\n🏥 Syncing patient facts...")
        patients = db.query(Patient).filter(Patient.is_active).all()
        for patient in patients:
            try:
                sync_patient_access(patient)
                print(f"✅ Synced patient access for {patient.name}")
            except Exception as e:
                print(f"❌ Failed to sync patient access for {patient.name}: {e}")

        # Sync all documents
        print("\n📄 Syncing document facts...")
        documents = db.query(Document).all()
        for document in documents:
            try:
                sync_document_access(document)
                print(f"✅ Synced document access for '{document.title}'")
            except Exception as e:
                print(f"❌ Failed to sync document access for '{document.title}': {e}")

        # Sync all embeddings
        print("\n🧮 Syncing embedding facts...")
        embeddings = db.query(Embedding).all()
        for embedding in embeddings:
            try:
                sync_embedding_access(embedding)
                print(f"✅ Synced embedding access for embedding {embedding.id}")
            except Exception as e:
                print(
                    f"❌ Failed to sync embedding access for embedding {embedding.id}: {e}"
                )

        print("\n🎉 OSO fact synchronization completed!")
        print(f"   Admin users: {len(admin_users)}")
        print(f"   Patients: {len(patients)}")
        print(f"   Documents: {len(documents)}")
        print(f"   Embeddings: {len(embeddings)}")

    finally:
        db.close()


def main() -> None:
    """Main function."""
    print("🔐 OSO Cloud Fact Synchronization")
    print("=" * 50)

    try:
        # Initialize OSO Cloud connection
        initialize_oso()

        # Synchronize all facts
        sync_all_facts()

        print("\n✅ All facts synchronized successfully!")

    except Exception as e:
        print(f"\n❌ Fact synchronization failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
