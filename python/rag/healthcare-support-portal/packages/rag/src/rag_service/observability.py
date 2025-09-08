"""
Observability module for RAG service using Galileo 2.0 and structured logging.
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

import structlog
from fastapi import Request

# Import Galileo modules correctly
from galileo import GalileoLogger, galileo_context
import os

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

# Galileo logging enabled flag
galileo_enabled: bool = False
galileo_logger: GalileoLogger = None


def initialize_observability():
    """Initialize all observability components."""
    global galileo_enabled, galileo_logger

    logger.info("Initializing observability components")

    # Read Galileo configuration from settings
    galileo_api_key = settings.galileo_api_key
    galileo_project_name = settings.galileo_project_name

    # Initialize Galileo logging if enabled and API key is provided
    if settings.galileo_enabled and galileo_api_key and galileo_api_key.strip():
        try:
            # Set Galileo environment variables for the modern API
            os.environ["GALILEO_API_KEY"] = galileo_api_key
            os.environ["GALILEO_PROJECT_NAME"] = galileo_project_name
            os.environ["GALILEO_ENVIRONMENT"] = settings.galileo_environment

            # Initialize GalileoLogger
            galileo_logger = GalileoLogger(project=galileo_project_name, log_stream="rag-service")

            galileo_enabled = True
            logger.info(
                "Galileo logging initialized successfully",
                project=galileo_project_name,
                environment=settings.galileo_environment,
            )
        except Exception as e:
            logger.error("Failed to initialize Galileo logging", error=str(e))
            galileo_enabled = False
            galileo_logger = None
    else:
        logger.info("Galileo observability disabled or API key not configured")
        galileo_enabled = False
        galileo_logger = None


@asynccontextmanager
async def rag_query_context(query_type: str, user_role: str, department: str = None, query_id: str = None):
    """Context manager for RAG query observability."""
    if query_id is None:
        query_id = str(uuid.uuid4())

    start_time = time.time()
    trace = None

    try:
        # Log query start
        logger.info(
            "RAG query started", query_type=query_type, user_role=user_role, department=department, query_id=query_id
        )

        # Start Galileo trace if enabled
        if galileo_enabled and galileo_logger:
            try:
                # Start a session if not already started
                session_id = galileo_logger.start_session(name=f"RAG-{query_type}", external_id=query_id)

                # Start a trace
                trace = galileo_logger.start_trace(
                    input=f"RAG {query_type} query",
                    name=f"RAG Query - {query_type}",
                    tags=[query_type, user_role, department] if department else [query_type, user_role],
                    metadata={
                        "query_type": query_type,
                        "user_role": user_role,
                        "department": department,
                        "query_id": query_id,
                    },
                )
            except Exception as e:
                logger.warning("Failed to start Galileo trace", error=str(e))

        yield query_id

    except Exception as e:
        # Log error
        logger.error(
            "RAG query failed",
            query_type=query_type,
            user_role=user_role,
            department=department,
            query_id=query_id,
            error=str(e),
        )

        # Add error information to Galileo trace if enabled
        if galileo_enabled and galileo_logger and trace:
            try:
                # Add an agent span to capture the error
                galileo_logger.add_agent_span(
                    input=f"RAG {query_type} query",
                    output=f"Error: {str(e)}",
                    name=f"RAG Error - {query_type}",
                    metadata={"error_type": type(e).__name__, "error": str(e)},
                    tags=["error", query_type],
                )
            except Exception as galileo_error:
                logger.warning("Failed to log error to Galileo", error=str(galileo_error))

        raise

    finally:
        # Calculate duration
        duration = time.time() - start_time
        duration_ns = int(duration * 1_000_000_000)

        # Log query completion
        logger.info(
            "RAG query completed",
            query_type=query_type,
            user_role=user_role,
            department=department,
            query_id=query_id,
            duration=duration,
        )

        # Conclude Galileo trace if enabled
        if galileo_enabled and galileo_logger and trace:
            try:
                galileo_logger.conclude(output="RAG query completed", duration_ns=duration_ns)
                galileo_logger.flush()
            except Exception as galileo_error:
                logger.warning("Failed to conclude Galileo trace", error=str(galileo_error))


@asynccontextmanager
async def embedding_generation_context(model: str, chunk_count: int, operation_id: str = None):
    """Context manager for embedding generation observability."""
    if operation_id is None:
        operation_id = str(uuid.uuid4())

    start_time = time.time()

    try:
        logger.info("Embedding generation started", model=model, chunk_count=chunk_count, operation_id=operation_id)

        # Log to Galileo
        log_galileo_event(
            event_type="embedding_generation_started",
            event_data={
                "model": model,
                "chunk_count": chunk_count,
                "operation_id": operation_id,
                "timestamp": start_time,
            },
        )

        yield operation_id

    except Exception as e:
        logger.error(
            "Embedding generation failed", model=model, chunk_count=chunk_count, operation_id=operation_id, error=str(e)
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
                "timestamp": time.time(),
            },
        )

        raise

    finally:
        duration = time.time() - start_time

        logger.info(
            "Embedding generation completed",
            model=model,
            chunk_count=chunk_count,
            operation_id=operation_id,
            duration=duration,
        )

        # Log completion to Galileo
        log_galileo_event(
            event_type="embedding_generation_completed",
            event_data={
                "model": model,
                "chunk_count": chunk_count,
                "operation_id": operation_id,
                "duration": duration,
                "timestamp": time.time(),
            },
        )


@asynccontextmanager
async def vector_search_context(result_count: int, similarity_threshold: float, search_id: str = None):
    """Context manager for vector search observability."""
    if search_id is None:
        search_id = str(uuid.uuid4())

    start_time = time.time()

    try:
        logger.info(
            "Vector search started",
            result_count=result_count,
            similarity_threshold=similarity_threshold,
            search_id=search_id,
        )

        # Log to Galileo
        log_galileo_event(
            event_type="vector_search_started",
            event_data={
                "result_count": result_count,
                "similarity_threshold": similarity_threshold,
                "search_id": search_id,
                "timestamp": start_time,
            },
        )

        yield search_id

    except Exception as e:
        logger.error(
            "Vector search failed",
            result_count=result_count,
            similarity_threshold=similarity_threshold,
            search_id=search_id,
            error=str(e),
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
                "timestamp": time.time(),
            },
        )

        raise

    finally:
        duration = time.time() - start_time

        logger.info(
            "Vector search completed",
            result_count=result_count,
            similarity_threshold=similarity_threshold,
            search_id=search_id,
            duration=duration,
        )

        # Log completion to Galileo
        log_galileo_event(
            event_type="vector_search_completed",
            event_data={
                "result_count": result_count,
                "similarity_threshold": similarity_threshold,
                "search_id": search_id,
                "duration": duration,
                "timestamp": time.time(),
            },
        )


@asynccontextmanager
async def ai_response_context(model: str, token_count: int, response_id: str = None):
    """Context manager for AI response generation observability."""
    if response_id is None:
        response_id = str(uuid.uuid4())

    start_time = time.time()

    try:
        logger.info("AI response generation started", model=model, token_count=token_count, response_id=response_id)

        # Log to Galileo
        log_galileo_event(
            event_type="ai_response_generation_started",
            event_data={
                "model": model,
                "token_count": token_count,
                "response_id": response_id,
                "timestamp": start_time,
            },
        )

        yield response_id

    except Exception as e:
        logger.error(
            "AI response generation failed", model=model, token_count=token_count, response_id=response_id, error=str(e)
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
                "timestamp": time.time(),
            },
        )

        raise

    finally:
        duration = time.time() - start_time

        logger.info(
            "AI response generation completed",
            model=model,
            token_count=token_count,
            response_id=response_id,
            duration=duration,
        )

        # Log completion to Galileo
        log_galileo_event(
            event_type="ai_response_generation_completed",
            event_data={
                "model": model,
                "token_count": token_count,
                "response_id": response_id,
                "duration": duration,
                "timestamp": time.time(),
            },
        )


def log_llm_call(
    input_text: str,
    output_text: str,
    model: str,
    num_input_tokens: int = None,
    num_output_tokens: int = None,
    total_tokens: int = None,
    duration_ns: int = None,
    temperature: float = None,
):
    """Log an LLM call to Galileo."""
    if galileo_enabled and galileo_logger:
        try:
            galileo_logger.add_llm_span(
                input=input_text,
                output=output_text,
                model=model,
                name=f"LLM Call - {model}",
                num_input_tokens=num_input_tokens,
                num_output_tokens=num_output_tokens,
                total_tokens=total_tokens,
                duration_ns=duration_ns,
                temperature=temperature,
                tags=["llm", str(model)],
                metadata={
                    "model": str(model),
                    "temperature": str(temperature) if temperature else "0.7",
                    "input_tokens": str(num_input_tokens) if num_input_tokens else "unknown",
                    "output_tokens": str(num_output_tokens) if num_output_tokens else "unknown",
                    "total_tokens": str(total_tokens) if total_tokens else "unknown",
                },
            )
            logger.debug("LLM call logged to Galileo", model=model)
        except Exception as e:
            logger.warning("Failed to log LLM call to Galileo", error=str(e))


def log_retriever_call(query: str, documents: list, duration_ns: int = None):
    """Log a retriever call to Galileo."""
    if galileo_enabled and galileo_logger:
        try:
            galileo_logger.add_retriever_span(
                input=query,
                output=documents,
                name="Document Retrieval",
                duration_ns=duration_ns,
                tags=["retriever", "rag"],
                metadata={
                    "query": str(query),
                    "document_count": str(len(documents)) if documents else "0",
                    "duration_ms": str(duration_ns / 1_000_000) if duration_ns else "unknown",
                },
            )
            logger.debug("Retriever call logged to Galileo", doc_count=len(documents) if documents else 0)
        except Exception as e:
            logger.warning("Failed to log retriever call to Galileo", error=str(e))


def log_document_upload(document_type: str, department: str, file_size: int, document_id: int):
    """Log document upload metrics."""
    logger.info(
        "Document uploaded",
        document_type=document_type,
        department=department,
        file_size=file_size,
        document_id=document_id,
    )

    # Log to Galileo
    log_galileo_event(
        event_type="document_uploaded",
        event_data={
            "document_type": document_type,
            "department": department,
            "file_size": file_size,
            "document_id": document_id,
            "timestamp": time.time(),
        },
    )


def log_embeddings_stored(document_id: int, chunk_count: int):
    """Log embeddings storage metrics."""
    logger.info("Embeddings stored", document_id=document_id, chunk_count=chunk_count)

    # Log to Galileo
    log_galileo_event(
        event_type="embeddings_stored",
        event_data={"document_id": document_id, "chunk_count": chunk_count, "timestamp": time.time()},
    )


def log_galileo_event(event_type: str, event_data: Dict[str, Any], user_id: str = None, session_id: str = None):
    """Log event to Galileo using the GalileoLogger."""
    if galileo_enabled and galileo_logger:
        try:
            # Create a workflow span for general events
            message = event_data.get("query", event_data.get("message", f"{event_type} event"))

            # Add a workflow span to capture the event
            # Convert all metadata values to strings for Galileo validation
            metadata = {
                "event_type": str(event_type),
                "user_id": str(user_id) if user_id else "unknown",
                "session_id": str(session_id or str(uuid.uuid4())),
                "timestamp": str(time.time()),
            }

            # Convert event_data values to strings
            for key, value in event_data.items():
                metadata[key] = str(value) if value is not None else "null"

            galileo_logger.add_workflow_span(
                input=message,
                output=f"Event: {event_type}",
                name=event_type,
                metadata=metadata,
                tags=[event_type, "event"],
            )

            logger.debug("Event logged to Galileo", event_type=event_type, user_id=user_id, session_id=session_id)
        except Exception as e:
            logger.error("Failed to log event to Galileo", event_type=event_type, error=str(e))


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
                        "timestamp": time.time(),
                    },
                )
                raise
            finally:
                duration = time.time() - start_time

                logger.info(
                    "HTTP request completed",
                    method=request.method,
                    path=request.url.path,
                    duration=duration,
                    status_code=getattr(scope, "status_code", 500),
                )

                # Log to Galileo
                log_galileo_event(
                    event_type="http_request_completed",
                    event_data={
                        "method": request.method,
                        "path": request.url.path,
                        "duration": duration,
                        "status_code": getattr(scope, "status_code", 500),
                        "timestamp": time.time(),
                    },
                )
        else:
            await self.app(scope, receive, send)
