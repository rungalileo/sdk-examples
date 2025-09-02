"""
Observability module for RAG service using Galileo 2.0 and structured logging.
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

import structlog
from fastapi import Request
from galileo import Galileo

from .config import settings

# Initialize structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Galileo client
galileo_client: Optional[Galileo] = None


def initialize_observability():
    """Initialize all observability components."""
    global galileo_client
    
    logger.info("Initializing observability components")
    
    # Initialize Galileo 2.0
    if settings.galileo_enabled and settings.galileo_api_key:
        try:
            galileo_client = Galileo(
                api_key=settings.galileo_api_key,
                project_name=settings.galileo_project_name,
                environment=settings.galileo_environment
            )
            logger.info("Galileo 2.0 client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Galileo client", error=str(e))
    else:
        logger.info("Galileo observability disabled or API key not configured")


@asynccontextmanager
async def rag_query_context(
    query_type: str,
    user_role: str,
    department: str = None,
    query_id: str = None
):
    """Context manager for RAG query observability."""
    if query_id is None:
        query_id = str(uuid.uuid4())
    
    start_time = time.time()
    
    try:
        # Log query start
        logger.info(
            "RAG query started",
            query_type=query_type,
            user_role=user_role,
            department=department,
            query_id=query_id
        )
        
        # Log to Galileo
        log_galileo_event(
            event_type="rag_query_started",
            event_data={
                "query_type": query_type,
                "user_role": user_role,
                "department": department,
                "query_id": query_id,
                "timestamp": start_time
            }
        )
        
        yield query_id
        
    except Exception as e:
        # Log error
        logger.error(
            "RAG query failed",
            query_type=query_type,
            user_role=user_role,
            department=department,
            query_id=query_id,
            error=str(e)
        )
        
        # Log error to Galileo
        log_galileo_event(
            event_type="rag_query_failed",
            event_data={
                "query_type": query_type,
                "user_role": user_role,
                "department": department,
                "query_id": query_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": time.time()
            }
        )
        
        raise
    
    finally:
        # Calculate duration
        duration = time.time() - start_time
        
        # Log query completion
        logger.info(
            "RAG query completed",
            query_type=query_type,
            user_role=user_role,
            department=department,
            query_id=query_id,
            duration=duration
        )
        
        # Log completion to Galileo
        log_galileo_event(
            event_type="rag_query_completed",
            event_data={
                "query_type": query_type,
                "user_role": user_role,
                "department": department,
                "query_id": query_id,
                "duration": duration,
                "timestamp": time.time()
            }
        )


@asynccontextmanager
async def embedding_generation_context(
    model: str,
    chunk_count: int,
    operation_id: str = None
):
    """Context manager for embedding generation observability."""
    if operation_id is None:
        operation_id = str(uuid.uuid4())
    
    start_time = time.time()
    
    try:
        logger.info(
            "Embedding generation started",
            model=model,
            chunk_count=chunk_count,
            operation_id=operation_id
        )
        
        # Log to Galileo
        log_galileo_event(
            event_type="embedding_generation_started",
            event_data={
                "model": model,
                "chunk_count": chunk_count,
                "operation_id": operation_id,
                "timestamp": start_time
            }
        )
        
        yield operation_id
        
    except Exception as e:
        logger.error(
            "Embedding generation failed",
            model=model,
            chunk_count=chunk_count,
            operation_id=operation_id,
            error=str(e)
        )
        
        # Log error to Galileo
        log_galileo_event(
            event_type="embedding_generation_failed",
            event_data={
                "model": model,
                "chunk_count": chunk_count,
                "operation_id": operation_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": time.time()
            }
        )
        
        raise
    
    finally:
        duration = time.time() - start_time
        
        logger.info(
            "Embedding generation completed",
            model=model,
            chunk_count=chunk_count,
            operation_id=operation_id,
            duration=duration
        )
        
        # Log completion to Galileo
        log_galileo_event(
            event_type="embedding_generation_completed",
            event_data={
                "model": model,
                "chunk_count": chunk_count,
                "operation_id": operation_id,
                "duration": duration,
                "timestamp": time.time()
            }
        )


@asynccontextmanager
async def vector_search_context(
    result_count: int,
    similarity_threshold: float,
    search_id: str = None
):
    """Context manager for vector search observability."""
    if search_id is None:
        search_id = str(uuid.uuid4())
    
    start_time = time.time()
    
    try:
        logger.info(
            "Vector search started",
            result_count=result_count,
            similarity_threshold=similarity_threshold,
            search_id=search_id
        )
        
        # Log to Galileo
        log_galileo_event(
            event_type="vector_search_started",
            event_data={
                "result_count": result_count,
                "similarity_threshold": similarity_threshold,
                "search_id": search_id,
                "timestamp": start_time
            }
        )
        
        yield search_id
        
    except Exception as e:
        logger.error(
            "Vector search failed",
            result_count=result_count,
            similarity_threshold=similarity_threshold,
            search_id=search_id,
            error=str(e)
        )
        
        # Log error to Galileo
        log_galileo_event(
            event_type="vector_search_failed",
            event_data={
                "result_count": result_count,
                "similarity_threshold": similarity_threshold,
                "search_id": search_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": time.time()
            }
        )
        
        raise
    
    finally:
        duration = time.time() - start_time
        
        logger.info(
            "Vector search completed",
            result_count=result_count,
            similarity_threshold=similarity_threshold,
            search_id=search_id,
            duration=duration
        )
        
        # Log completion to Galileo
        log_galileo_event(
            event_type="vector_search_completed",
            event_data={
                "result_count": result_count,
                "similarity_threshold": similarity_threshold,
                "search_id": search_id,
                "duration": duration,
                "timestamp": time.time()
            }
        )


@asynccontextmanager
async def ai_response_context(
    model: str,
    token_count: int,
    response_id: str = None
):
    """Context manager for AI response generation observability."""
    if response_id is None:
        response_id = str(uuid.uuid4())
    
    start_time = time.time()
    
    try:
        logger.info(
            "AI response generation started",
            model=model,
            token_count=token_count,
            response_id=response_id
        )
        
        # Log to Galileo
        log_galileo_event(
            event_type="ai_response_generation_started",
            event_data={
                "model": model,
                "token_count": token_count,
                "response_id": response_id,
                "timestamp": start_time
            }
        )
        
        yield response_id
        
    except Exception as e:
        logger.error(
            "AI response generation failed",
            model=model,
            token_count=token_count,
            response_id=response_id,
            error=str(e)
        )
        
        # Log error to Galileo
        log_galileo_event(
            event_type="ai_response_generation_failed",
            event_data={
                "model": model,
                "token_count": token_count,
                "response_id": response_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": time.time()
            }
        )
        
        raise
    
    finally:
        duration = time.time() - start_time
        
        logger.info(
            "AI response generation completed",
            model=model,
            token_count=token_count,
            response_id=response_id,
            duration=duration
        )
        
        # Log completion to Galileo
        log_galileo_event(
            event_type="ai_response_generation_completed",
            event_data={
                "model": model,
                "token_count": token_count,
                "response_id": response_id,
                "duration": duration,
                "timestamp": time.time()
            }
        )


def log_document_upload(
    document_type: str,
    department: str,
    file_size: int,
    document_id: int
):
    """Log document upload metrics."""
    logger.info(
        "Document uploaded",
        document_type=document_type,
        department=department,
        file_size=file_size,
        document_id=document_id
    )
    
    # Log to Galileo
    log_galileo_event(
        event_type="document_uploaded",
        event_data={
            "document_type": document_type,
            "department": department,
            "file_size": file_size,
            "document_id": document_id,
            "timestamp": time.time()
        }
    )


def log_embeddings_stored(
    document_id: int,
    chunk_count: int
):
    """Log embeddings storage metrics."""
    logger.info(
        "Embeddings stored",
        document_id=document_id,
        chunk_count=chunk_count
    )
    
    # Log to Galileo
    log_galileo_event(
        event_type="embeddings_stored",
        event_data={
            "document_id": document_id,
            "chunk_count": chunk_count,
            "timestamp": time.time()
        }
    )


def log_galileo_event(
    event_type: str,
    event_data: Dict[str, Any],
    user_id: str = None,
    session_id: str = None
):
    """Log event to Galileo 2.0."""
    if galileo_client:
        try:
            galileo_client.log_event(
                event_type=event_type,
                event_data=event_data,
                user_id=user_id,
                session_id=session_id
            )
            logger.debug(
                "Event logged to Galileo",
                event_type=event_type,
                user_id=user_id,
                session_id=session_id
            )
        except Exception as e:
            logger.error(
                "Failed to log event to Galileo",
                event_type=event_type,
                error=str(e)
            )


class ObservabilityMiddleware:
    """FastAPI middleware for observability."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            start_time = time.time()
            
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                # Log error to Galileo
                log_galileo_event(
                    event_type="http_request_failed",
                    event_data={
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "timestamp": time.time()
                    }
                )
                raise
            finally:
                duration = time.time() - start_time
                
                logger.info(
                    "HTTP request completed",
                    method=request.method,
                    path=request.url.path,
                    duration=duration,
                    status_code=getattr(scope, "status_code", 500)
                )
                
                # Log to Galileo
                log_galileo_event(
                    event_type="http_request_completed",
                    event_data={
                        "method": request.method,
                        "path": request.url.path,
                        "duration": duration,
                        "status_code": getattr(scope, "status_code", 500),
                        "timestamp": time.time()
                    }
                )
        else:
            await self.app(scope, receive, send)
