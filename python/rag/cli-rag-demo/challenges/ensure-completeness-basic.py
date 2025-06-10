import os
from pathlib import Path
from dotenv import load_dotenv
from galileo.logger import GalileoLogger
from galileo.openai import openai
from rich.console import Console
from document_store_basic import DocumentStoreBasic, format_documents
from galileo import galileo_context

# Find the .env file in the parent directory
current_dir = Path(__file__).resolve().parent
dotenv_path = ".env"

# Load the .env file
load_dotenv(dotenv_path)

EXAMPLE_QUESTION = "Who discovered penicillin and what were the key details of this discovery?"

SYSTEM_PROMPT = "You are a helpful assistant. Answer questions based on the provided document."


class Prompts:
    BASIC = """Question: {query}

Document:
{documents}

Please provide an answer based on the document above."""


def query(question: str):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))

    # Basic approach: single document, no reranking
    current_dir = Path(__file__).resolve().parent
    custom_docs_path = current_dir / "penicillin_documents.txt"

    store = DocumentStoreBasic(
        source="custom",
        custom_documents_path=str(custom_docs_path),
        num_docs=1,  # Only one document
        chunk_size=1000,  # Larger chunks, less precise
    )
    docs = store.search(question)

    prompt = Prompts.BASIC.format(query=question, documents=format_documents(docs))

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
        log_stream="basic_approach",
    ):
        console = Console()
        console.print("\nBasic Completeness Demo")
        console.print("\nUsing example question:", EXAMPLE_QUESTION)

        response = query(EXAMPLE_QUESTION)
        console.print("\nResponse:")
        console.print(response)


if __name__ == "__main__":
    main()
