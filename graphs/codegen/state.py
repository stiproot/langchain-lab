import operator
from typing import (
    Sequence,
    TypedDict,
    Annotated,
    Annotated,
)
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class RootState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
