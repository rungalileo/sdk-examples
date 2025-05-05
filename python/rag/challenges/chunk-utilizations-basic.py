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
root_dir = current_dir.parent
dotenv_path = root_dir / ".env"

# Load the .env file
load_dotenv(dotenv_path)

# Debug: Print environment variables
print("Environment variables:")
print("GALILEO_PROJECT:", os.getenv("GALILEO_PROJECT"))
print("GALILEO_API_KEY:", os.getenv("GALILEO_API_KEY"))
print("GALILEO_BASE_URL:", os.getenv("GALILEO_BASE_URL"))

EXAMPLE_QUESTION = "What are the fundamental concepts and operations in arithmetic, and how are they used in mathematics?"


class Prompts:
    BASIC = """Answer the following question based on the provided documents.
    
Question: {query}

Documents:
{documents}"""


def query(question: str):

    # Debug: Print logger configuration
    print("\nLogger configuration:")
    print("Project:", os.getenv("GALILEO_PROJECT", "chunk-utilization"))
    print("Log stream: basic_approach")

    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
    )

    # Basic approach: more results but no reranking
    docs = DocumentStore(num_docs=500, k=5, use_reranking=False).search(question)

    prompt = Prompts.BASIC.format(query=question, documents=format_documents(docs))

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Explain mathematical concepts in a straightforward way.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def main():
    with galileo_context(
        project=os.getenv("GALILEO_PROJECT", "chunk-utilization"),
        log_stream="basic_approach",
    ):
        console = Console()
        console.print("\nBasic Chunk Utilization Demo")
        console.print("\nUsing example question:", EXAMPLE_QUESTION)
        console.print("\nResponse:")
        console.print(query(EXAMPLE_QUESTION))


if __name__ == "__main__":
    main()
