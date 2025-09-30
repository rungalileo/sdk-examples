"""
Tool for retrieving information from Pinecone vector database.
Falls back to mock data if Pinecone is not configured.
"""

from typing import Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class RetrievalInput(BaseModel):
    """Input schema for document retrieval."""

    query: str = Field(description="Search query")
    k: int = Field(default=3, description="Number of documents to retrieve")


class PineconeRetrievalTool(BaseTool):
    """Tool for retrieving telecom plan and service information."""

    name: str = "pinecone_retrieval"
    description: str = "Retrieve telecom plans and service information from knowledge base"
    args_schema: type[BaseModel] = RetrievalInput

    def __init__(self, index_name: str = "telecom-plans"):
        super().__init__()
        self._index_name = index_name
        self._vector_store = None

        # Try to initialize Pinecone, fallback to mock if unavailable
        try:
            from langchain_pinecone import PineconeVectorStore
            from langchain_openai import OpenAIEmbeddings

            self._embeddings = OpenAIEmbeddings()
            self._vector_store = PineconeVectorStore(index_name=self._index_name, embedding=self._embeddings)
        except Exception:
            # Use mock data if Pinecone not configured
            pass

    def _get_mock_results(self, query: str) -> str:
        """Return mock plan data when Pinecone unavailable."""

        mock_data = {
            "unlimited": """
Premium Unlimited 5G Plan:
- Price: $85/month
- Data: Truly unlimited
- Speed: 5G where available
- Hotspot: 50GB high-speed
- Perks: Netflix Basic included
""",
            "family": """
Family Share Plans:
- 2 lines: $120/month (100GB shared)
- 3 lines: $150/month (150GB shared)
- 4+ lines: $180/month (200GB shared)
- All plans include unlimited talk/text
""",
            "business": """
Business Plans:
- Essential: $45/line (25GB)
- Professional: $65/line (50GB)
- Enterprise: $85/line (unlimited)
- All include priority support
""",
            "international": """
International Features:
- Global Pass: $10/day (200+ countries)
- International Plus: +$15/month
- Unlimited texting to 200+ countries
- Call rates from $0.25/minute
""",
        }

        # Simple keyword matching
        query_lower = query.lower()
        for key, value in mock_data.items():
            if key in query_lower:
                return value

        # Default response
        return """
Available Plans:
- Premium Unlimited 5G ($85/month)
- Family Share (from $120/month)
- Business Plans (from $45/line)
- Basic Essential ($65/month)

Ask about specific plans for details.
"""

    def _run(self, query: str, k: int = 3) -> str:
        """Execute retrieval from vector store or mock data."""

        if self._vector_store:
            try:
                # Try Pinecone retrieval
                results = self._vector_store.similarity_search(query, k=k)

                if not results:
                    return "No relevant information found."

                formatted = []
                for i, doc in enumerate(results, 1):
                    formatted.append(f"Result {i}:\n{doc.page_content}\n")

                return "\n".join(formatted)

            except Exception:
                # Fallback to mock on error
                pass

        # Use mock data
        return self._get_mock_results(query)
