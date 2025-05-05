from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Optional
import re
from pathlib import Path


class DocumentStoreBasic:
    def __init__(
        self,
        source: str = "custom",
        custom_documents_path: Optional[str] = None,
        num_docs: int = 1,  # Only return 1 document
        chunk_size: int = 1000,  # Larger chunks, less precise
    ):
        self.source = source
        self.documents = []
        self.num_docs = num_docs

        # Use a simpler embedding model
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

        # Load documents based on source
        if source == "custom":
            if not custom_documents_path:
                raise ValueError(
                    "custom_documents_path must be provided when source is 'custom'"
                )
            self._load_custom_documents(custom_documents_path, chunk_size)
        else:
            raise ValueError(f"Unsupported source: {source}. Use 'custom'")

        if not self.documents:
            raise ValueError("No documents were successfully loaded")

        print(f"Processed {len(self.documents)} chunks")

        self._build_index()

    def _load_custom_documents(self, documents_path: str, chunk_size: int):
        """Helper method to load custom documents from a file"""
        documents_path = Path(documents_path)
        if not documents_path.exists():
            raise FileNotFoundError(
                f"Custom documents file not found: {documents_path}"
            )

        with open(documents_path, "r") as f:
            text = f.read()

        # Simple chunking by paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        # Process and store documents with basic chunking
        for i, paragraph in enumerate(paragraphs):
            if not paragraph or len(paragraph) < 50:
                continue

            # Simple chunking - just split by sentences
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            chunks = []
            current_chunk = []
            current_length = 0

            for sentence in sentences:
                if current_length + len(sentence) > chunk_size and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence]
                    current_length = len(sentence)
                else:
                    current_chunk.append(sentence)
                    current_length += len(sentence)

            if current_chunk:
                chunks.append(" ".join(current_chunk))

            for j, chunk in enumerate(chunks):
                self.documents.append(
                    {
                        "text": chunk,
                        "metadata": {
                            "source": f"Document {i+1}",
                            "chunk_id": j,
                            "total_chunks": len(chunks),
                            "relevance": "medium",
                            "length": len(chunk),
                        },
                    }
                )

    def _build_index(self):
        print("Building basic FAISS index...")
        texts = [doc["text"] for doc in self.documents]
        self.embeddings = self.encoder.encode(texts)
        dimension = self.embeddings.shape[1]

        # Use basic L2 distance instead of cosine similarity
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype("float32"))
        print("Index built successfully")

    def search(self, query: str) -> list:
        # Encode the query
        query_vector = self.encoder.encode([query])[0]
        query_vector = query_vector.reshape(1, -1)

        # Get only one result
        distances, indices = self.index.search(
            query_vector.astype("float32"), self.num_docs
        )

        # Process results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            doc = self.documents[idx].copy()
            doc["metadata"] = doc["metadata"].copy()
            doc["metadata"]["score"] = float(
                1 / (1 + distance)
            )  # Simple distance to score conversion
            results.append(doc)

        return results


def format_documents(documents: list) -> str:
    return "\n\n".join(
        f"Document {i+1}:\n{doc['text']}" for i, doc in enumerate(documents)
    )
