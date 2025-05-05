import os
from pathlib import Path
from dotenv import load_dotenv
from galileo.logger import GalileoLogger
from galileo.openai import openai
from rich.console import Console
from document_store import DocumentStore, format_documents
from galileo import galileo_context

# Find the .env file in the parent directory
current_dir = Path(__file__).resolve().parent
dotenv_path = ".env"

# Load the .env file
load_dotenv(dotenv_path)

EXAMPLE_QUESTION = (
    "Who discovered penicillin and what were the key details of this discovery?"
)

SYSTEM_PROMPT = """You are a knowledgeable science historian tasked with providing comprehensive answers by analyzing and synthesizing information from multiple provided documents.

IMPORTANT INSTRUCTIONS:
1. You MUST use ALL relevant information from the retrieved documents in your response.
2. For each key fact or detail you mention, explicitly cite the source document number (e.g., "As shown in Document 1...").
3. If multiple documents contain related information, synthesize them into a cohesive explanation while citing all relevant sources.
4. Do not omit any significant details present in the retrieved documents.
5. If documents present different aspects of the same information, combine them to provide a complete picture.
6. Pay attention to the relevance scores of documents - higher scores often indicate more pertinent information.
7. Structure your response to build from foundational facts to more detailed information, citing the relevant documents throughout.

Your response should demonstrate thorough analysis and integration of ALL information from the retrieved documents, making clear how each source contributed to the complete answer."""


class Prompts:
    ENHANCED = """Question: {query}

Documents:
{documents}

IMPORTANT: Your response must:
1. Use ALL relevant information from the documents above
2. Cite specific document numbers for each fact
3. Synthesize information from multiple documents when they contain related details
4. Do not omit any significant details present in the documents
5. Structure your response to build from foundational facts to more detailed information"""


def format_documents_with_citations(documents: list) -> str:
    return "\n\n".join(
        f"Document {i+1} (Source: {doc['metadata']['source']}, Relevance: {doc['metadata']['relevance']}, "
        f"Score: {doc['metadata'].get('combined_score', doc['metadata'].get('score', 'N/A')):.3f}):\n{doc['text']}"
        for i, doc in enumerate(documents)
    )


def query(question: str):
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
    )

    # Enhanced approach: more documents with reranking
    current_dir = Path(__file__).resolve().parent
    custom_docs_path = current_dir / "penicillin_documents.txt"

    store = DocumentStore(
        source="custom",
        custom_documents_path=str(custom_docs_path),
        num_docs=10,  # More documents
        use_reranking=True,  # Use reranking
        reranking_threshold=0.6,
    )
    docs = store.search(question)

    prompt = Prompts.ENHANCED.format(
        query=question, documents=format_documents_with_citations(docs)
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def main():
    with galileo_context(
        project=os.getenv("GALILEO_PROJECT", "ensure-completeness"),
        log_stream="enhanced_approach",
    ):
        console = Console()
        console.print("\nEnhanced Completeness Demo")
        console.print("\nUsing example question:", EXAMPLE_QUESTION)

        response = query(EXAMPLE_QUESTION)
        console.print("\nResponse:")
        console.print(response)


if __name__ == "__main__":
    main()
