import sys
from pathlib import Path

# Add the common package to Python path
common_path = Path(__file__).parent.parent.parent.parent.parent / "common" / "src"
sys.path.insert(0, str(common_path))

from galileo.openai import openai
from common.models import Document, Embedding
from common.oso_sync import sync_embedding_access
from sqlalchemy import text
from sqlalchemy.orm import Session


async def generate_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """Generate embedding for a given text using OpenAI (Galileo instrumented)."""
    try:
        # Import settings to get API key
        from ..config import settings

        client = openai.OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []


async def store_document_embeddings(
    document: Document,
    chunks: list[str],
    db: Session,
    model: str = "text-embedding-3-small",
) -> bool:
    """Generate and store embeddings for document chunks."""
    try:
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding_vector = await generate_embedding(chunk, model)

            if not embedding_vector:
                continue

            # Create embedding record
            db_embedding = Embedding(
                document_id=document.id,
                content_chunk=chunk,
                embedding_vector=embedding_vector,
                chunk_index=i,
            )

            db.add(db_embedding)
            db.commit()
            db.refresh(db_embedding)

            # Sync OSO facts for new embedding
            try:
                sync_embedding_access(db_embedding)
            except Exception as e:
                print(f"Warning: Failed to sync OSO facts for embedding {db_embedding.id}: {e}")

        return True

    except Exception as e:
        print(f"Error storing embeddings: {e}")
        db.rollback()
        return False


async def similarity_search(
    query_text: str,
    db: Session,
    limit: int = 5,
    similarity_threshold: float = 0.1,
    document_ids: list[int] | None = None,
) -> list[dict]:
    """
    Perform similarity search using pgvector.
    """
    import time

    start_time = time.time()

    try:
        # Generate query embedding
        query_embedding = await generate_embedding(query_text)

        if not query_embedding:
            return []

        # Build SQL query for similarity search
        base_query = """
        SELECT 
            e.id,
            e.document_id,
            e.content_chunk,
            e.chunk_index,
            d.title,
            d.document_type,
            d.department,
            d.is_sensitive,
            1 - (e.embedding_vector <=> :query_vector) as similarity
        FROM embeddings e
        JOIN documents d ON e.document_id = d.id
        WHERE 1 - (e.embedding_vector <=> :query_vector) > :threshold
        """

        # Convert query embedding to proper format for pgvector
        params = {
            "query_vector": str(query_embedding),
            "threshold": similarity_threshold,
        }

        # Add document ID filter if provided
        if document_ids:
            placeholders = ",".join([f":doc_id_{i}" for i in range(len(document_ids))])
            base_query += f" AND e.document_id IN ({placeholders})"
            for i, doc_id in enumerate(document_ids):
                params[f"doc_id_{i}"] = doc_id

        base_query += " ORDER BY similarity DESC LIMIT :limit"
        params["limit"] = limit

        # Execute query with proper parameter binding
        result = db.execute(text(base_query), params)
        rows = result.fetchall()

        # Convert to list of dictionaries
        results = []
        for row in rows:
            results.append(
                {
                    # Frontend-compatible field names
                    "id": row[1],  # document_id → id
                    "title": row[4],  # document_title → title
                    "content_chunk": row[2],
                    "document_type": row[5],
                    "department": row[6],
                    "similarity_score": float(row[8]),  # similarity → similarity_score
                    "created_at": "",  # Will be populated by document data if needed
                    # Keep internal fields for backend processing
                    "embedding_id": row[0],
                    "document_id": row[1],  # Keep for internal use
                    "chunk_index": row[3],
                    "document_title": row[4],  # Keep for internal use
                    "is_sensitive": row[7],
                    "similarity": float(row[8]),  # Keep for internal use
                }
            )

        # Log retriever call to Galileo
        try:
            from ..observability import log_retriever_call

            duration_ns = int((time.time() - start_time) * 1_000_000_000)

            # Format results for Galileo logging
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "document_title": result["title"],
                        "content_chunk": result["content_chunk"][:200] + "..." if len(result["content_chunk"]) > 200 else result["content_chunk"],
                        "similarity_score": result["similarity_score"],
                        "document_type": result["document_type"],
                        "department": result["department"],
                    }
                )

            log_retriever_call(query=query_text, documents=formatted_results, duration_ns=duration_ns)
        except Exception as log_error:
            print(f"Warning: Failed to log retriever call to Galileo: {log_error}")

        return results

    except Exception as e:
        print(f"Error in similarity search: {e}")
        return []


async def regenerate_document_embeddings(document: Document, db: Session, model: str = "text-embedding-3-small") -> dict:
    """
    Regenerate embeddings for an existing document.
    Returns status dict with success and message.
    """
    try:
        from ..utils.text_processing import chunk_text

        # Delete existing embeddings for this document
        db.query(Embedding).filter(Embedding.document_id == document.id).delete()
        db.commit()

        # Create new chunks from document content
        chunks = chunk_text(
            document.content,
            chunk_size=500,  # Default chunk size
            chunk_overlap=50,  # Default overlap
        )

        # Generate and store new embeddings
        success = await store_document_embeddings(document, chunks, db, model)

        if success:
            return {
                "success": True,
                "message": f"Successfully regenerated {len(chunks)} embeddings for document {document.id}",
                "chunks_created": len(chunks),
            }
        else:
            return {
                "success": False,
                "message": f"Failed to regenerate embeddings for document {document.id}",
                "chunks_created": 0,
            }

    except Exception as e:
        print(f"Error regenerating embeddings for document {document.id}: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}", "chunks_created": 0}


async def get_embedding_status(document_id: int, db: Session) -> dict:
    """
    Get embedding status for a document.
    """
    try:
        embedding_count = db.query(Embedding).filter(Embedding.document_id == document_id).count()

        return {
            "document_id": document_id,
            "has_embeddings": embedding_count > 0,
            "embedding_count": embedding_count,
        }
    except Exception as e:
        print(f"Error getting embedding status for document {document_id}: {e}")
        return {
            "document_id": document_id,
            "has_embeddings": False,
            "embedding_count": 0,
            "error": str(e),
        }


def combine_chunks_for_context(search_results: list[dict], max_tokens: int = 6000) -> str:
    """
    Combine relevant chunks into context for RAG, respecting token limits.
    """
    context_parts = []
    current_tokens = 0

    for result in search_results:
        chunk = result["content_chunk"]
        title = result["document_title"]

        # Simple token estimation (more accurate would use tiktoken)
        chunk_tokens = len(chunk.split()) * 1.3  # Rough estimation

        if current_tokens + chunk_tokens > max_tokens:
            break

        context_part = f"Document: {title}\nContent: {chunk}\n---\n"
        context_parts.append(context_part)
        current_tokens += chunk_tokens

    return "\n".join(context_parts)
