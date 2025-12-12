"""
Retrieval Service - A separate FastAPI service that handles information retrieval.

Run this service with: uvicorn retrieval_service:app --reload --port 8000
"""

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from galileo import log
from galileo.middleware.tracing import TracingMiddleware

load_dotenv()

app = FastAPI(title="Retrieval Service")

# Add Galileo tracing middleware to handle distributed tracing headers
app.add_middleware(TracingMiddleware)


class RetrievalRequest(BaseModel):
    query: str


class RetrievalResponse(BaseModel):
    results: list[str]


@log(span_type="retriever")
def retrieval_service(query: str) -> list[str]:
    """
    Retrieval agent that searches through a knowledge base.
    In a real scenario, this would query a vector database or search engine.
    The @log decorator automatically handles distributed tracing headers if present.
    """
    # Mock knowledge base
    knowledge_base = {
        "birthplace": ["Galileo Galilei was born in Pisa, Italy in 1564"],
        "profession": ["Galileo Galilei taught geometry, mechanics, and astronomy at the University of Padua for many years"],
        "research": ["Using improved telescopes that he built, Galileo Galilei made scientific observations that transformed our understanding of the universe."],
    }
    
    # Simple keyword-based retrieval (in production, use vector search)
    results = []
    query_lower = query.lower()
    for category, facts in knowledge_base.items():
        if category in query_lower or any(word in query_lower for word in ["work", "company", "location", "education"]):
            results.extend(facts)
    
    return results[:3]  # Return top 3 results


@app.post("/retrieve", response_model=RetrievalResponse)
@log
async def retrieve_endpoint(request: RetrievalRequest):
    """
    Endpoint that receives retrieval requests from the orchestrator.
    The TracingMiddleware automatically handles distributed tracing headers.
    """
    # The @log decorator automatically uses the trace context set by middleware
    results = retrieval_service(request.query)
    return RetrievalResponse(results=results)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

