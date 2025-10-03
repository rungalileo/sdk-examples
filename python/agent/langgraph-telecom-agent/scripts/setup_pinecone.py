"""
This script sets up a Pinecone index for storing and retrieving telecom documentation from the `source-docs` folder.

The script will upload:
- Telecom plan information (pricing, features, comparisons)
- Network troubleshooting guides
- Technical documentation

To use this, you will need to have the following environment variables set in the .env file:
- `PINECONE_API_KEY`: Your Pinecone API key.
- `OPENAI_API_KEY`: Your OpenAI API key (for embeddings).
"""

import asyncio
import os

from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from pinecone import Pinecone

load_dotenv()

EMBEDDINGS = OpenAIEmbeddings()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


def load_documents(path):
    """Load all markdown documents from source-docs folder"""
    loader = DirectoryLoader(
        path, glob="*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    return documents


def chunk_documents(documents):
    """Chunk documents semantically"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=[
            "\n\n",  # Double newlines (paragraphs)
            "\n",  # Single newlines
            " ",  # Spaces
            ".",  # Sentences
            ",",  # Clauses
            "\u200b",  # Zero-width space
            "\uff0c",  # Fullwidth comma
            "\u3001",  # Ideographic comma
            "\uff0e",  # Fullwidth full stop
            "\u3002",  # Ideographic full stop
            "",  # Character-level
        ],
        is_separator_regex=False,
    )

    chunked_docs = text_splitter.split_documents(documents)
    return chunked_docs


def setup_pinecone_index(index_name: str) -> None:
    """Initialize Pinecone and create/connect to index"""
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Check if index exists, create if not
    if index_name not in pc.list_indexes().names():
        print(f"Creating new index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embeddings dimension
            metric="cosine",
            spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
        )
    else:
        print(f"Index {index_name} already exists")


def check_index_has_data(index) -> bool:
    """Check if the index already contains data"""
    try:
        stats = index.describe_index_stats()
        total_vector_count = stats.get("total_vector_count", 0)
        return total_vector_count > 0
    except Exception as e:
        print(f"Error checking index stats: {e}")
        return False


def upload_to_pinecone(
    chunked_docs, index_name: str, force_upload: bool = False
) -> PineconeVectorStore:
    """Upload chunked documents to Pinecone"""

    # Check if index has data and we're not forcing upload
    if not force_upload:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(index_name)

        if check_index_has_data(index):
            print(f"Index {index_name} already contains data. Skipping upload.")
            print("Use force_upload=True to overwrite existing data.")
            return PineconeVectorStore(index_name=index_name, embedding=EMBEDDINGS)

    # Create vector store and upload
    print(f"Uploading {len(chunked_docs)} chunks to Pinecone...")
    vector_store = PineconeVectorStore.from_documents(
        documents=chunked_docs, embedding=EMBEDDINGS, index_name=index_name
    )

    print(f"Successfully uploaded {len(chunked_docs)} document chunks to Pinecone")
    return vector_store


def test_retrieval(index_name: str, query: str):
    """Test document retrieval from Pinecone"""
    vector_store = PineconeVectorStore(index_name=index_name, embedding=EMBEDDINGS)

    # Test similarity search
    results = vector_store.similarity_search(query, k=3)

    print(f"\nTest query: '{query}'")
    print(f"Found {len(results)} relevant chunks:")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc.page_content[:200]}...")


telecom_documents = [
    {
        "index_name": "telecom",
        "path": "source-docs",
        "test_query": "unlimited data plan",
    }
]


async def main():
    """
    Main function to process and upload documents asynchronously
    """

    for doc in telecom_documents:
        index_name = doc["index_name"]
        path = doc["path"]
        test_query = doc["test_query"]

        print(f"Loading documents for {index_name} folder...")
        loaded_documents = load_documents(path)
        print(f"Loaded {len(loaded_documents)} documents")

        print(f"Chunking documents for {index_name}...")
        chunked_docs = chunk_documents(loaded_documents)
        print(f"Created {len(chunked_docs)} chunks")

        print(f"Setting up Pinecone for {index_name}...")
        setup_pinecone_index(index_name)

        # Only upload if index is new or doesn't have data
        print(f"Uploading to Pinecone for {index_name}...")
        _ = upload_to_pinecone(chunked_docs, index_name=index_name)

    # Wait for Pinecone to index the data
    print("Waiting for Pinecone to index the data...")
    await asyncio.sleep(30)

    # Test retrieval for each index
    for doc in telecom_documents:
        index_name = doc["index_name"]
        test_query = doc["test_query"]
        print(f"Testing retrieval for {index_name} with query: '{test_query}'")
        test_retrieval(index_name=index_name, query=test_query)

    print("✅ Document processing and upload complete!")


if __name__ == "__main__":
    asyncio.run(main())
