"""
A tool for retrieving information about credit scores from a financial services knowledge base.
"""

from typing_extensions import override

from langchain.tools import BaseTool


class CreditScoreTool(BaseTool):
    """
    CreditScoreTool is a tool for retrieving relevant information about credit scores from a financial services knowledge base.
    """

    name: str = "credit_score_retrieval"
    description: str = "Retrieve relevant information about credit scores from the financial services knowledge base"

    @override
    def _run(self) -> str:
        """
        Always return a credit score of 550 for testing purposes.
        """
        return "Your credit score is 550"
