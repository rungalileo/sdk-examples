"""
OSO Cloud Fact Synchronization Utilities
Manages authorization facts in OSO Cloud to keep them in sync with database state.
"""

import logging

try:
    from oso_cloud import Value
except ImportError:
    print("Warning: oso_cloud not installed. OSO fact synchronization will be disabled.")
    Value = None

from .db import SessionLocal
from .models import Document, Embedding, Patient, User

logger = logging.getLogger(__name__)


def get_oso_client():
    """Get the OSO client instance from sqlalchemy-oso-cloud."""
    if Value is None:
        raise ImportError("oso_cloud is not available")

    try:
        from sqlalchemy_oso_cloud import get_oso

        return get_oso()
    except ImportError as e:
        logger.error(f"Failed to import OSO client: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to get OSO client: {e}")
        raise


def sync_admin_global_access(user: User) -> bool:
    """
    Sync global admin access facts for an admin user.
    Creates has_role facts for admin access to all resources.
    """
    if user.role != "admin":
        logger.warning(f"User {user.id} is not an admin, skipping global access sync")
        return False

    try:
        oso = get_oso_client()
        db = SessionLocal()

        try:
            with oso.batch() as tx:
                user_value = Value("User", str(user.id))

                # Admin access to all patients
                patients = db.query(Patient).filter(Patient.is_active).all()
                for patient in patients:
                    tx.insert(
                        (
                            "has_role",
                            user_value,
                            "admin",
                            Value("Patient", str(patient.id)),
                        )
                    )

                # Admin access to all documents
                documents = db.query(Document).all()
                for doc in documents:
                    tx.insert(
                        (
                            "has_role",
                            user_value,
                            "admin",
                            Value("Document", str(doc.id)),
                        )
                    )

                # Admin access to all embeddings
                embeddings = db.query(Embedding).all()
                for embed in embeddings:
                    tx.insert(
                        (
                            "has_role",
                            user_value,
                            "admin",
                            Value("Embedding", str(embed.id)),
                        )
                    )

                # Admin access to all users
                users = db.query(User).filter(User.is_active).all()
                for other_user in users:
                    tx.insert(
                        (
                            "has_role",
                            user_value,
                            "admin",
                            Value("User", str(other_user.id)),
                        )
                    )

            logger.info(f"Synced global admin access for user {user.id}")
            return True

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to sync global admin access for user {user.id}: {e}")
        return False


def remove_admin_global_access(user: User) -> bool:
    """Remove all admin access facts for a user."""
    try:
        oso = get_oso_client()

        with oso.batch() as tx:
            user_value = Value("User", str(user.id))
            # Remove all admin roles for this user
            tx.delete(("has_role", user_value, "admin", None))

        logger.info(f"Removed all admin access for user {user.id}")
        return True

    except Exception as e:
        logger.error(f"Failed to remove admin access for user {user.id}: {e}")
        return False


def sync_patient_access(patient: Patient) -> bool:
    """
    Sync patient access facts based on doctor assignment and department.
    Creates assigned_doctor and department_nurse facts.
    """
    try:
        oso = get_oso_client()
        db = SessionLocal()

        try:
            with oso.batch() as tx:
                patient_value = Value("Patient", str(patient.id))

                # Doctor assignment fact
                if patient.assigned_doctor_id:
                    doctor_value = Value("User", str(patient.assigned_doctor_id))
                    tx.insert(("has_role", doctor_value, "assigned_doctor", patient_value))

                # Department nurse facts - all nurses in the patient's department
                if patient.department:
                    nurses = (
                        db.query(User)
                        .filter(
                            User.role == "nurse",
                            User.department == patient.department,
                            User.is_active,
                        )
                        .all()
                    )

                    for nurse in nurses:
                        nurse_value = Value("User", str(nurse.id))
                        tx.insert(("has_role", nurse_value, "department_nurse", patient_value))

                # Admin access facts for all admins
                admins = db.query(User).filter(User.role == "admin", User.is_active).all()

                for admin in admins:
                    admin_value = Value("User", str(admin.id))
                    tx.insert(("has_role", admin_value, "admin", patient_value))

            logger.info(f"Synced patient access for patient {patient.id}")
            return True

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to sync patient access for patient {patient.id}: {e}")
        return False


def remove_patient_access(patient_id: int) -> bool:
    """Remove all access facts for a patient."""
    try:
        oso = get_oso_client()

        with oso.batch() as tx:
            patient_value = Value("Patient", str(patient_id))
            # Remove all roles for this patient
            tx.delete(("has_role", None, None, patient_value))

        logger.info(f"Removed all access facts for patient {patient_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to remove patient access facts for patient {patient_id}: {e}")
        return False


def sync_document_access(document: Document) -> bool:
    """
    Sync document access facts based on ownership, patient relationships, and department.
    """
    try:
        oso = get_oso_client()
        db = SessionLocal()

        try:
            with oso.batch() as tx:
                doc_value = Value("Document", str(document.id))

                # Owner fact - document creator has full control
                if document.created_by_id:
                    owner_value = Value("User", str(document.created_by_id))
                    tx.insert(("has_role", owner_value, "owner", doc_value))

                # Patient doctor fact - if document is linked to a patient
                if document.patient_id:
                    patient = db.query(Patient).filter(Patient.id == document.patient_id).first()
                    if patient and patient.assigned_doctor_id:
                        doctor_value = Value("User", str(patient.assigned_doctor_id))
                        tx.insert(("has_role", doctor_value, "patient_doctor", doc_value))

                # Department staff fact - for non-sensitive documents
                if document.department and not document.is_sensitive:
                    dept_users = db.query(User).filter(User.department == document.department, User.is_active).all()

                    for user in dept_users:
                        user_value = Value("User", str(user.id))
                        tx.insert(("has_role", user_value, "department_staff", doc_value))

                # Admin access facts for all admins
                admins = db.query(User).filter(User.role == "admin", User.is_active).all()

                for admin in admins:
                    admin_value = Value("User", str(admin.id))
                    tx.insert(("has_role", admin_value, "admin", doc_value))

            logger.info(f"Synced document access for document {document.id}")
            return True

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to sync document access for document {document.id}: {e}")
        return False


def remove_document_access(document_id: int) -> bool:
    """Remove all access facts for a document."""
    try:
        oso = get_oso_client()

        with oso.batch() as tx:
            doc_value = Value("Document", str(document_id))
            # Remove all roles for this document
            tx.delete(("has_role", None, None, doc_value))

        logger.info(f"Removed all access facts for document {document_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to remove document access facts for document {document_id}: {e}")
        return False


def sync_embedding_access(embedding: Embedding) -> bool:
    """
    Sync embedding access facts - only admins can access embeddings.
    """
    try:
        oso = get_oso_client()
        db = SessionLocal()

        try:
            with oso.batch() as tx:
                embed_value = Value("Embedding", str(embedding.id))

                # Admin access facts for all admins
                admins = db.query(User).filter(User.role == "admin", User.is_active).all()

                for admin in admins:
                    admin_value = Value("User", str(admin.id))
                    tx.insert(("has_role", admin_value, "admin", embed_value))

            logger.info(f"Synced embedding access for embedding {embedding.id}")
            return True

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to sync embedding access for embedding {embedding.id}: {e}")
        return False


def remove_embedding_access(embedding_id: int) -> bool:
    """Remove all access facts for an embedding."""
    try:
        oso = get_oso_client()

        with oso.batch() as tx:
            embed_value = Value("Embedding", str(embedding_id))
            # Remove all roles for this embedding
            tx.delete(("has_role", None, None, embed_value))

        logger.info(f"Removed all access facts for embedding {embedding_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to remove embedding access facts for embedding {embedding_id}: {e}")
        return False


def sync_user_role_change(user: User, old_role: str | None = None) -> bool:
    """
    Handle user role changes - remove old role facts and add new ones.
    """
    try:
        oso = get_oso_client()

        # If user was previously an admin, remove global access
        if old_role == "admin" and user.role != "admin":
            remove_admin_global_access(user)

        # If user became an admin, add global access
        if user.role == "admin" and old_role != "admin":
            sync_admin_global_access(user)

        # Resync all patient access (for department nurse changes)
        db = SessionLocal()
        try:
            patients = db.query(Patient).filter(Patient.is_active).all()
            for patient in patients:
                # Remove old nurse access for this user
                user_value = Value("User", str(user.id))
                patient_value = Value("Patient", str(patient.id))

                oso.delete(("has_role", user_value, "department_nurse", patient_value))

                # Add new nurse access if applicable
                if user.role == "nurse" and patient.department == user.department:
                    oso.insert(("has_role", user_value, "department_nurse", patient_value))
        finally:
            db.close()

        logger.info(f"Synced role change for user {user.id}: {old_role} -> {user.role}")
        return True

    except Exception as e:
        logger.error(f"Failed to sync role change for user {user.id}: {e}")
        return False


def sync_department_change(user: User, old_department: str | None = None) -> bool:
    """
    Handle user department changes - update department-based access.
    """
    try:
        oso = get_oso_client()
        db = SessionLocal()

        try:
            user_value = Value("User", str(user.id))

            # Remove old department nurse access
            if old_department and user.role == "nurse":
                old_patients = db.query(Patient).filter(Patient.department == old_department, Patient.is_active).all()

                with oso.batch() as tx:
                    for patient in old_patients:
                        patient_value = Value("Patient", str(patient.id))
                        tx.delete(("has_role", user_value, "department_nurse", patient_value))

            # Add new department nurse access
            if user.department and user.role == "nurse":
                new_patients = db.query(Patient).filter(Patient.department == user.department, Patient.is_active).all()

                with oso.batch() as tx:
                    for patient in new_patients:
                        patient_value = Value("Patient", str(patient.id))
                        tx.insert(("has_role", user_value, "department_nurse", patient_value))

        finally:
            db.close()

        logger.info(f"Synced department change for user {user.id}: {old_department} -> {user.department}")
        return True

    except Exception as e:
        logger.error(f"Failed to sync department change for user {user.id}: {e}")
        return False


def full_resync() -> bool:
    """
    Perform a complete resynchronization of all facts.
    Useful for initial setup or recovery from sync issues.
    """
    try:
        db = SessionLocal()

        try:
            logger.info("Starting full fact resynchronization...")

            # Clear all existing facts (be very careful with this!)
            # oso.delete(("has_role", None, None, None))  # Uncomment if needed

            # Sync all users
            users = db.query(User).filter(User.is_active).all()
            for user in users:
                if user.role == "admin":
                    sync_admin_global_access(user)

            # Sync all patients
            patients = db.query(Patient).filter(Patient.is_active).all()
            for patient in patients:
                sync_patient_access(patient)

            # Sync all documents
            documents = db.query(Document).all()
            for document in documents:
                sync_document_access(document)

            # Sync all embeddings
            embeddings = db.query(Embedding).all()
            for embedding in embeddings:
                sync_embedding_access(embedding)

            logger.info("Full fact resynchronization completed successfully")
            return True

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed during full resynchronization: {e}")
        return False
