import operator
from typing import (
    Sequence,
    TypedDict,
    Annotated,
    Annotated,
)
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    user_input: str
    messages: Annotated[Sequence[BaseMessage], operator.add]


class C4ContextAgentState(AgentState):
    c4_context_diagram_path: str


class C4ContainerAgentState(AgentState):
    c4_context_diagram_path: str
    c4_container_diagram_path: str


class RootState(TypedDict):
    user_input: str
    c4_context_diagram_path: str
    c4_container_diagram_path: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
