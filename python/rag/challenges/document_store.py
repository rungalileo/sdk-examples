from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
from datasets import load_dataset
import numpy as np
from galileo import log
from typing import List, Dict, Optional, Union
import re
from pathlib import Path


class DocumentStore:
    def __init__(
        self,
        source: str = "wikipedia",  # "wikipedia" or "custom"
        custom_documents_path: Optional[str] = None,
        num_docs: int = 1000,
        k: int = 3,
        chunk_size: int = 512,
        reranking_threshold: float = 0.6,
        use_reranking: bool = False,
        reranking_multiplier: int = 4,
        wikipedia_query: Optional[str] = None,
    ):
        self.source = source
        self.documents = []
        self.k = k
        self.use_reranking = use_reranking
        self.reranking_threshold = reranking_threshold
        self.reranking_multiplier = reranking_multiplier

        # Initialize encoder and cross-encoder
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        if use_reranking:
            print("Loading cross-encoder for reranking...")
            self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        # Load documents based on source
        if source == "wikipedia":
            try:
                # Load Wikipedia dataset with configurable parameters
                print(f"Loading {num_docs} Wikipedia articles...")
                dataset = load_dataset(
                    "wikipedia",
                    "20220301.simple",
                    split=f"train[:{num_docs}]",
                    trust_remote_code=True,
                )

                if wikipedia_query:
                    # Use the query to filter relevant articles
                    query_terms = wikipedia_query.lower().split()
                    filtered_articles = []

                    for article in dataset:
                        article_text = article["text"].lower()
                        # Check if any of the query terms appear in the article
                        if any(term in article_text for term in query_terms):
                            filtered_articles.append(article)

                    if not filtered_articles:
                        print(f"No Wikipedia articles found for query: {wikipedia_query}")
                        if custom_documents_path:
                            print("Falling back to custom documents...")
                            self._load_custom_documents(custom_documents_path, chunk_size)
                        else:
                            raise ValueError("No documents found and no custom documents path provided")
                    else:
                        dataset = filtered_articles[:num_docs]
                        self._process_wikipedia_documents(dataset, chunk_size)

                else:
                    self._process_wikipedia_documents(dataset, chunk_size)

            except Exception as e:
                print(f"Error loading Wikipedia articles: {e}")
                if custom_documents_path:
                    print("Falling back to custom documents...")
                    self._load_custom_documents(custom_documents_path, chunk_size)
                else:
                    raise

        elif source == "custom":
            if not custom_documents_path:
                raise ValueError("custom_documents_path must be provided when source is 'custom'")
            self._load_custom_documents(custom_documents_path, chunk_size)

        else:
            raise ValueError(f"Unsupported source: {source}. Use 'wikipedia' or 'custom'")

        if not self.documents:
            raise ValueError("No documents were successfully loaded")

        print(f"Processed {len(self.documents)} chunks from {len(set(doc['metadata']['source'] for doc in self.documents))} documents")
        print(f"Average chunk length: {sum(doc['metadata']['length'] for doc in self.documents) / len(self.documents):.0f} characters")

        self._build_index()

    def _process_wikipedia_documents(self, dataset, chunk_size: int):
        """Process Wikipedia documents into chunks"""
        for item in dataset:
            # Skip empty or very short articles
            if not item["text"] or len(item["text"]) < 100:
                continue

            # Split text into chunks
            chunks = self._chunk_text(item["text"], chunk_size)

            for i, chunk in enumerate(chunks):
                self.documents.append(
                    {
                        "text": chunk,
                        "metadata": {
                            "source": item["title"],
                            "chunk_id": i,
                            "total_chunks": len(chunks),
                            "relevance": "medium",
                            "length": len(chunk),
                            "url": item.get("url", ""),
                            "original_length": len(item["text"]),
                        },
                    }
                )

    def _load_custom_documents(self, documents_path: str, chunk_size: int):
        """Helper method to load custom documents from a file"""
        documents_path = Path(documents_path)
        if not documents_path.exists():
            raise FileNotFoundError(f"Custom documents file not found: {documents_path}")

        with open(documents_path, "r") as f:
            text = f.read()

        # Split into paragraphs and process as documents
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        # Process and store documents with chunking
        for i, paragraph in enumerate(paragraphs):
            # Skip empty or very short paragraphs
            if not paragraph or len(paragraph) < 50:
                continue

            # Split text into chunks
            chunks = self._chunk_text(paragraph, chunk_size)

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
                            "url": "",
                            "original_length": len(paragraph),
                        },
                    }
                )

    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks of approximately chunk_size tokens.
        Uses sentence boundaries where possible to maintain context.
        """
        # First split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            # Rough estimation of tokens (words + punctuation)
            sentence_length = len(sentence.split())

            if current_length + sentence_length > chunk_size and current_chunk:
                # If adding this sentence would exceed chunk_size, save current chunk
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _build_index(self):
        print("Building FAISS index...")
        texts = [doc["text"] for doc in self.documents]
        self.embeddings = self.encoder.encode(texts)
        dimension = self.embeddings.shape[1]

        # Use L2 normalization for better similarity search
        faiss.normalize_L2(self.embeddings)

        # Create an index that's optimized for cosine similarity
        self.index = faiss.IndexFlatIP(dimension)  # Inner product is equivalent to cosine similarity for normalized vectors
        self.index.add(self.embeddings.astype("float32"))
        print("Index built successfully")

    def _rerank_documents(self, docs: List[Dict], query: str) -> List[Dict]:
        """
        Rerank documents using a cross-encoder model, which provides more accurate
        relevance scoring by considering query and document together.
        """
        # Create pairs of (query, document) for cross-encoder scoring
        pairs = [(query, doc["text"]) for doc in docs]

        # Get cross-encoder scores
        cross_scores = self.cross_encoder.predict(pairs)

        # Normalize scores to 0-1 range for consistency
        min_score = min(cross_scores)
        max_score = max(cross_scores)
        score_range = max_score - min_score

        reranked_docs = []
        for doc, score in zip(docs, cross_scores):
            # Normalize score to 0-1 range
            normalized_score = (score - min_score) / score_range if score_range > 0 else 0.5

            if normalized_score >= self.reranking_threshold:
                doc["metadata"]["combined_score"] = normalized_score
                doc["metadata"]["relevance"] = "high" if normalized_score > 0.8 else "medium" if normalized_score > 0.6 else "low"
                reranked_docs.append(doc)

        # Sort by combined score
        reranked_docs.sort(key=lambda x: x["metadata"]["combined_score"], reverse=True)
        return reranked_docs[: self.k]

    @log(span_type="retriever")
    def search(self, query: str) -> list:
        # Encode and normalize the query
        query_vector = self.encoder.encode([query])[0]
        query_vector = query_vector / np.linalg.norm(query_vector)
        query_vector = query_vector.reshape(1, -1)

        # Get more initial results if using reranking
        initial_k = self.k * self.reranking_multiplier if self.use_reranking else self.k
        scores, indices = self.index.search(query_vector.astype("float32"), initial_k)

        # Process results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            doc = self.documents[idx].copy()
            doc["metadata"] = doc["metadata"].copy()
            doc["metadata"]["score"] = float(score)
            results.append(doc)

        # Apply reranking if enabled
        if self.use_reranking:
            print(f"Reranking top {initial_k} results...")
            return self._rerank_documents(results, query)
        else:
            # For basic search, just update relevance based on score
            for doc in results:
                doc["metadata"]["relevance"] = "high" if doc["metadata"]["score"] > 0.8 else "medium" if doc["metadata"]["score"] > 0.6 else "low"
            return results[: self.k]


def format_documents(documents: list) -> str:
    return "\n\n".join(
        f"Document {i+1} (Source: {doc['metadata']['source']}, Chunk {doc['metadata']['chunk_id'] + 1}/{doc['metadata']['total_chunks']}, "
        f"Relevance: {doc['metadata']['relevance']}, "
        f"Score: {doc['metadata'].get('combined_score', doc['metadata'].get('score', 'N/A')):.3f}):\n{doc['text']}"
        for i, doc in enumerate(documents)
    )
