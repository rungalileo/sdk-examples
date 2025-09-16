import re

import tiktoken


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove special characters but keep medical terminology
    text = re.sub(r"[^\w\s\-\.\,\:\;\(\)\/]", "", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks for better context preservation.
    """
    # Initialize tokenizer
    encoding = tiktoken.get_encoding("cl100k_base")

    # Tokenize the text
    tokens = encoding.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        # Define the end of the current chunk
        end = start + chunk_size

        # Extract chunk tokens
        chunk_tokens = tokens[start:end]

        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens)

        chunks.append(chunk_text.strip())

        # Move start position with overlap
        start = end - chunk_overlap

        # Break if we've processed all tokens
        if end >= len(tokens):
            break

    return chunks


def extract_keywords(text: str) -> list[str]:
    """Extract potential medical keywords from text."""
    # Simple keyword extraction - in production, use more sophisticated NLP
    medical_patterns = [
        r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # Proper nouns (conditions, medications)
        r"\b\d+\s*mg\b",  # Dosages
        r"\b\d+\s*ml\b",  # Volumes
        r"\bICD[-\s]?\d+\b",  # ICD codes
        r"\bCPT[-\s]?\d+\b",  # CPT codes
    ]

    keywords = []
    for pattern in medical_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend(matches)

    return list(set(keywords))  # Remove duplicates


def calculate_token_count(text: str) -> int:
    """Calculate the number of tokens in a text."""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
