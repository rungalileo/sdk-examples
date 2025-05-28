from typing import TypedDict, Annotated, Optional

from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: Optional[str]
    english_response: Optional[str]
    spanish_response: Optional[str]
    hindi_response: Optional[str]
