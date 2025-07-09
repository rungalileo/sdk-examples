"""
A tool for retrieving information from the Pinecone vector database.
"""

from typing_extensions import override

from langchain.tools import BaseTool
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel, Field


class RetrievalInput(BaseModel):
    """
    RetrievalInput is a Pydantic model representing the input schema for a document retrieval operation.
    Attributes:
        query (str): The search query used to find relevant documents.
        k (int, optional): The number of documents to retrieve. Defaults to 3.
    """

    query: str = Field(description="The search query to find relevant documents")
    k: int = Field(default=3, description="Number of documents to retrieve")


class PineconeRetrievalTool(BaseTool):
    """
    PineconeRetrievalTool is a tool for retrieving relevant information from a financial services knowledge base using Pinecone as a vector store.
    """

    name: str = "pinecone_retrieval"
    description: str = "Retrieve relevant information from the financial services knowledge base"
    args_schema: type[BaseModel] = RetrievalInput  # type: ignore

    def __init__(self, index_name: str):
        super().__init__()
        self._embeddings = OpenAIEmbeddings()
        self._index_name = index_name
        self._vector_store = PineconeVectorStore(index_name=self._index_name, embedding=self._embeddings)

    @override
    def _run(self, query: str, k: int = 3) -> str:
        """Execute the retrieval"""
        try:
            # Perform similarity search
            results = self._vector_store.similarity_search(query, k=k)

            if not results:
                return "No relevant information found in the knowledge base."

            # Format the results
            formatted_results = []
            for i, doc in enumerate(results, 1):
                formatted_results.append(f"Document {i}:\n{doc.page_content}\n")

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error retrieving information: {str(e)}"
