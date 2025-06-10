from typing_extensions import List, TypedDict
from langchain_core.documents import Document


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
