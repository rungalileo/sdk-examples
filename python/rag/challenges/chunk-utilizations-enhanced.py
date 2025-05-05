import os
from pathlib import Path
from dotenv import load_dotenv
from galileo.logger import GalileoLogger
from galileo.openai import openai
from rich.console import Console
from document_store import DocumentStore, format_documents
from galileo import galileo_context
import numpy as np
from typing import List, Dict

# Find the .env file in the parent directory
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
dotenv_path = root_dir / ".env"

# Load the .env file
load_dotenv(dotenv_path)

EXAMPLE_QUESTION = "What are the fundamental concepts and operations in arithmetic, and how are they used in mathematics?"

SYSTEM_PROMPT = """You are a knowledgeable mathematics educator tasked with providing comprehensive answers by analyzing and synthesizing information from multiple provided documents.

IMPORTANT INSTRUCTIONS:
1. Cross-reference information between documents - identify and connect complementary or contrasting information.
2. For each concept you discuss, cite the specific documents that support your explanation (e.g., "As shown in Document 1 and expanded in Document 3...").
3. When multiple documents contain related information, explicitly connect their content (e.g., "While Document 2 introduces basic addition, Document 4 builds on this by...").
4. If documents present different aspects or perspectives of a concept, synthesize them into a cohesive explanation.
5. Pay attention to the relevance scores of documents - higher scores often indicate more pertinent information.
6. Ensure you consider and utilize information from all relevant documents in your response.
7. Structure your response to build from foundational concepts to more advanced applications, citing the relevant documents throughout.

Your response should demonstrate thorough analysis and integration of information from all relevant documents, making clear how different sources contributed to the complete answer. Explain mathematical concepts clearly, connect related ideas, and highlight fundamental principles while maintaining accuracy."""


class Prompts:
    ENHANCED = """Question: {query}

Documents:
{documents}"""


def format_documents_enhanced(documents: list) -> str:
    return "\n\n".join(
        f"Document {i+1} (Source: {doc['metadata']['source']}, Relevance: {doc['metadata']['relevance']}, "
        f"Score: {doc['metadata'].get('combined_score', doc['metadata'].get('score', 'N/A')):.3f}):\n{doc['text']}"
        for i, doc in enumerate(documents)
    )


def query(question: str):
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
    )

    # Enhanced approach: use reranking with more initial documents
    docs = DocumentStore(
        num_docs=500, k=5, use_reranking=True, reranking_threshold=0.6
    ).search(question)

    prompt = Prompts.ENHANCED.format(query=question, documents=format_documents(docs))

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
        project=os.getenv("GALILEO_PROJECT", "chunk-utilization"),
        log_stream="enhanced_approach",
    ):
        console = Console()
        console.print("\nEnhanced Chunk Utilization Demo")
        console.print("\nUsing example question:", EXAMPLE_QUESTION)

        console.print("\nResponse:")
        console.print(query(EXAMPLE_QUESTION))


if __name__ == "__main__":
    main()
