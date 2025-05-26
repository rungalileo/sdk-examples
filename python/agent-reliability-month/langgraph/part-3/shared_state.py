from typing import TypedDict, Annotated

from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
