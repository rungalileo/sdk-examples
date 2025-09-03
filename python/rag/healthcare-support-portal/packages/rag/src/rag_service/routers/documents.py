import sys
from pathlib import Path

# Add the common package to Python path
common_path = Path(__file__).parent.parent.parent.parent.parent / "common" / "src"
sys.path.insert(0, str(common_path))


from common.auth import get_current_user
from common.db import get_db
from common.models import Document, User
from common.oso_sync import remove_document_access, sync_document_access
from common.schemas import DocumentCreate, DocumentResponse
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session
from sqlalchemy_oso_cloud import authorized, get_oso

from ..utils.embeddings import (
    get_embedding_status,
    regenerate_document_embeddings,
    store_document_embeddings,
)
from ..utils.text_processing import chunk_text, clean_text
from ..observability import embedding_generation_context, log_document_upload, log_embeddings_stored, log_galileo_event, logger

router = APIRouter()


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    document_type: str | None = Query(None),
    department: str | None = Query(None),
):
    """
    List documents with Oso authorization filtering
    """
    # Use Oso Cloud to filter documents the current user can read
    # Add error handling for development when OSO is not available
    try:
        query = db.query(Document).options(authorized(current_user, "read", Document))
    except Exception as oso_error:
        logger.warning("OSO authorization failed, falling back to basic query", error=str(oso_error), user_role=current_user.role)
        # In development, fallback to showing documents based on role/department
        query = db.query(Document)
        if current_user.role != "admin":
            # Non-admins only see documents from their department
            query = query.filter(Document.department == current_user.department)

    # Apply optional filters
    if document_type:
        query = query.filter(Document.document_type == document_type)

    if department:
        query = query.filter(Document.department == department)

    # Apply pagination
    documents = query.offset(skip).limit(limit).all()

    logger.info(
        "Documents listed", user_role=current_user.role, document_type=document_type, department=department, count=len(documents), skip=skip, limit=limit
    )

    return documents


@router.get("/embedding-statuses")
async def get_all_embedding_statuses(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get embedding status for all documents the user can access
    """
    # Use Oso Cloud to filter documents the current user can read
    # Add error handling for development when OSO is not available
    try:
        authorized_documents = db.query(Document).options(authorized(current_user, "read", Document)).all()
    except Exception as oso_error:
        logger.warning("OSO authorization failed in embedding statuses, falling back to basic query", error=str(oso_error), user_role=current_user.role)
        # In development, fallback to showing documents based on role/department
        if current_user.role == "admin":
            authorized_documents = db.query(Document).all()
        else:
            authorized_documents = db.query(Document).filter(Document.department == current_user.department).all()

    statuses = {}
    for document in authorized_documents:
        embedding_status = await get_embedding_status(document.id, db)
        statuses[document.id] = embedding_status

    logger.info("Embedding statuses retrieved", user_role=current_user.role, documents_count=len(authorized_documents), statuses_count=len(statuses))

    return statuses


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get specific document with Oso authorization
    """
    oso = get_oso()

    # Get the document
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        logger.warning("Document not found", document_id=document_id, user_role=current_user.role)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Check authorization with OSO fallback
    try:
        oso.authorize(current_user, "read", document)
    except Exception as e:
        logger.warning(
            "OSO authorization failed for document access, checking basic authorization", document_id=document_id, user_role=current_user.role, error=str(e)
        )
        # Fallback authorization logic for development
        if current_user.role == "admin":
            # Admins can access any document
            pass
        elif current_user.department == document.department:
            # Users can access documents from their department
            pass
        else:
            # Access denied
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied - document not in your department")

    logger.info("Document accessed", document_id=document_id, user_role=current_user.role, document_type=document.document_type, department=document.department)

    return document


@router.post("/", response_model=DocumentResponse)
async def create_document(
    document_data: DocumentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new document
    """
    # Create document
    document = Document(
        title=document_data.title,
        content=document_data.content,
        document_type=document_data.document_type,
        department=document_data.department,
        is_sensitive=document_data.is_sensitive,
        created_by_id=current_user.id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Sync Oso facts
    sync_document_access(document)

    # Log document creation
    log_galileo_event(
        event_type="document_created",
        event_data={
            "document_id": document.id,
            "title": document.title,
            "document_type": document.document_type,
            "department": document.department,
            "is_sensitive": document.is_sensitive,
            "content_length": len(document.content),
        },
        user_id=str(current_user.id),
    )

    logger.info("Document created", document_id=document.id, user_role=current_user.role, document_type=document.document_type, department=document.department)

    return document


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = None,
    document_type: str = None,
    department: str = None,
    is_sensitive: bool = False,
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload and process a document file
    """
    settings = request.app.state.settings

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Clean and process text
    text_content = clean_text(content.decode("utf-8"))

    # Use filename as title if not provided
    if not title:
        title = file.filename

    # Create document
    document = Document(
        title=title,
        content=text_content,
        document_type=document_type or "unknown",
        department=department or current_user.department,
        is_sensitive=is_sensitive,
        created_by_id=current_user.id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Sync Oso facts
    sync_document_access(document)

    # Log document upload
    log_document_upload(document_type=document.document_type, department=document.department, file_size=file_size, document_id=document.id)

    # Generate embeddings with observability
    try:
        chunks = chunk_text(
            text_content,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        async with embedding_generation_context(model=settings.embedding_model, chunk_count=len(chunks)) as operation_id:

            success = await store_document_embeddings(
                document=document,
                chunks=chunks,
                db=db,
                model=settings.embedding_model,
            )

            if success:
                log_embeddings_stored(document_id=document.id, chunk_count=len(chunks))

                # Log to Galileo
                log_galileo_event(
                    event_type="document_uploaded_with_embeddings",
                    event_data={
                        "document_id": document.id,
                        "title": document.title,
                        "document_type": document.document_type,
                        "department": document.department,
                        "file_size": file_size,
                        "chunks_count": len(chunks),
                        "embedding_model": settings.embedding_model,
                        "operation_id": operation_id,
                    },
                    user_id=str(current_user.id),
                )

                logger.info(
                    "Document uploaded and embeddings generated successfully",
                    document_id=document.id,
                    user_role=current_user.role,
                    chunks_count=len(chunks),
                    operation_id=operation_id,
                )

                return {
                    "message": "Document uploaded and processed successfully",
                    "document_id": document.id,
                    "chunks_created": len(chunks),
                    "embedding_status": "completed",
                }
            else:
                logger.error("Failed to generate embeddings for uploaded document", document_id=document.id, user_role=current_user.role)

                return {"message": "Document uploaded but embedding generation failed", "document_id": document.id, "embedding_status": "failed"}

    except Exception as e:
        logger.error("Error processing uploaded document", document_id=document.id, user_role=current_user.role, error=str(e))

        # Log error to Galileo
        log_galileo_event(
            event_type="document_upload_error",
            event_data={"document_id": document.id, "title": document.title, "error": str(e), "error_type": type(e).__name__},
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}",
        )


@router.post("/{document_id}/regenerate-embeddings")
async def regenerate_embeddings(
    document_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Regenerate embeddings for a document
    """
    settings = request.app.state.settings

    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        logger.warning("Document not found for embedding regeneration", document_id=document_id, user_role=current_user.role)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Check authorization
    try:
        oso = get_oso()
        oso.authorize(current_user, "read", document)
    except Exception as e:
        logger.warning("Unauthorized embedding regeneration attempt", document_id=document_id, user_role=current_user.role, error=str(e))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Regenerate embeddings with observability
    try:
        chunks = chunk_text(
            document.content,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        async with embedding_generation_context(model=settings.embedding_model, chunk_count=len(chunks)) as operation_id:

            result = await regenerate_document_embeddings(
                document=document,
                db=db,
                model=settings.embedding_model,
            )

            if result["success"]:
                log_embeddings_stored(document_id=document.id, chunk_count=len(chunks))

                # Log to Galileo
                log_galileo_event(
                    event_type="embeddings_regenerated",
                    event_data={
                        "document_id": document.id,
                        "title": document.title,
                        "chunks_count": len(chunks),
                        "embedding_model": settings.embedding_model,
                        "operation_id": operation_id,
                    },
                    user_id=str(current_user.id),
                )

                logger.info(
                    "Document embeddings regenerated successfully",
                    document_id=document.id,
                    user_role=current_user.role,
                    chunks_count=len(chunks),
                    operation_id=operation_id,
                )

                return result
            else:
                logger.error("Failed to regenerate document embeddings", document_id=document.id, user_role=current_user.role, error=result["message"])

                return result

    except Exception as e:
        logger.error("Error regenerating document embeddings", document_id=document_id, user_role=current_user.role, error=str(e))

        # Log error to Galileo
        log_galileo_event(
            event_type="embedding_regeneration_error",
            event_data={"document_id": document_id, "error": str(e), "error_type": type(e).__name__},
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error regenerating embeddings: {str(e)}",
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a document
    """
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        logger.warning("Document not found for deletion", document_id=document_id, user_role=current_user.role)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Check authorization
    try:
        oso = get_oso()
        oso.authorize(current_user, "delete", document)
    except Exception as e:
        logger.warning("Unauthorized document deletion attempt", document_id=document_id, user_role=current_user.role, error=str(e))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Remove Oso facts
    remove_document_access(document)

    # Delete document
    db.delete(document)
    db.commit()

    # Log to Galileo
    log_galileo_event(
        event_type="document_deleted",
        event_data={"document_id": document_id, "title": document.title, "document_type": document.document_type, "department": document.department},
        user_id=str(current_user.id),
    )

    logger.info("Document deleted", document_id=document_id, user_role=current_user.role, document_type=document.document_type, department=document.department)

    return {"message": "Document deleted successfully"}
