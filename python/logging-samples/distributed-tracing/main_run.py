"""
Orchestrator Service - Client that coordinates the RAG pipeline.

This is a separate process that:
1. Determines what context is needed
2. Calls the retrieval service (separate process) via HTTP
3. Formats the context for the LLM
4. Calls the LLM with the retrieved context

Run the retrieval service first: uvicorn retrieval_service:app --reload --port 8000
Then run this: python main_distributed_tracing.py
"""

from dotenv import load_dotenv
import httpx
import asyncio
from pathlib import Path
from galileo import log, galileo_context, get_tracing_headers
from galileo import openai

load_dotenv()

# Initialize OpenAI client with Galileo wrapper for automatic tracing
openai_client = openai.OpenAI()

# Retrieval service URL (separate process)
RETRIEVAL_SERVICE_URL = "http://localhost:8000"


# ============================================================================
# ORCHESTRATOR SERVICE
# ============================================================================


@log
async def orchestrator_agent(question: str) -> str:
    """
    Orchestrator agent that:
    1. Determines what information is needed
    2. Calls the retrieval service (separate process) via HTTP with distributed tracing
    3. Formats the context for the LLM
    4. Calls the LLM with the retrieved context
    """
    # Step 1: Determine what information we need
    context_analysis = analyze_question(question)

    # Step 2: Call retrieval service via HTTP with distributed tracing
    # Get current trace and span IDs to pass to the retrieval service
    # Similar to LangSmith's get_current_run_tree().to_headers()
    try:
        headers = get_tracing_headers()
    except Exception as e:
        print(f"Error getting tracing headers: {e}")
        headers = {}

    async with httpx.AsyncClient(base_url=RETRIEVAL_SERVICE_URL, timeout=100.0) as client:
        try:
            response = await client.post(
                "/retrieve",
                json={"query": question},
                headers=headers,  # Distributed tracing headers
            )
            response.raise_for_status()
            retrieved_docs = response.json()["results"]
        except httpx.HTTPError as e:
            retrieved_docs = []

    # Step 3: Format context for LLM
    context = format_context(context_analysis, retrieved_docs)

    # Step 4: Call LLM with retrieved context
    # The galileo wrapped OpenAI client automatically logs LLM spans
    response = openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""Answer the user's question using only the provided context below.
If the context doesn't contain enough information, say so.

Context:
{context}""",
            },
            {"role": "user", "content": question},
        ],
        model="gpt-5-mini",
    )

    return response.choices[0].message.content


@log
def analyze_question(question: str) -> dict:
    """
    Analyzes the question to determine what type of information is needed.
    """
    question_lower = question.lower()

    analysis = {
        "needs_company_info": any(word in question_lower for word in ["company", "work", "employer"]),
        "needs_location_info": any(word in question_lower for word in ["location", "where", "city", "live"]),
        "needs_education_info": any(word in question_lower for word in ["education", "school", "degree", "study"]),
        "question_type": "factual",
    }

    return analysis


@log
def format_context(analysis: dict, docs: list[str]) -> str:
    formatted = f"Analysis: {analysis}\n\n"
    formatted += "Retrieved Documents:\n"
    for i, doc in enumerate(docs, 1):
        formatted += f"{i}. {doc}\n"
    return formatted


# ============================================================================
# MAIN EXECUTION
# ============================================================================


async def main():
    """Run the distributed tracing example"""

    questions = [
        "What did Galileo Galilei research?",
        "Where did Galileo Galilei work?",
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}")
        answer = await orchestrator_agent(question)
        print(f"Answer: {answer}\n")


if __name__ == "__main__":
    asyncio.run(main())
