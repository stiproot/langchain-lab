import operator
from typing import (
    Sequence,
    TypedDict,
    Annotated,
    Annotated,
)
from langchain_core.messages import BaseMessage


# # Define custom reducer (see more on this in the "Custom reducer" section below)
# def add_msgs(left: list[BaseMessage], right: list[BaseMessage]) -> list[BaseMessage]:
#     if not left:
#         left = []

#     if not right:
#         right = []

#     logs = left.copy()
#     left_id_to_idx = {log["id"]: idx for idx, log in enumerate(logs)}
#     # update if the new logs are already in the state, otherwise append
#     for log in right:
#         idx = left_id_to_idx.get(log["id"])
#         if idx is not None:
#             logs[idx] = log
#         else:
#             logs.append(log)
#     return logs


class AgentState(TypedDict):
    user_input: str
    global_messages: Annotated[Sequence[BaseMessage], operator.add]
    messages: Annotated[Sequence[BaseMessage], operator.add]


class C4ContextAgentState(AgentState):
    c4_context_diagram_path: str


class C4ContainerAgentState(AgentState):
    c4_context_diagram_path: str
    c4_container_diagram_path: str


class C4ComponentAgentState(AgentState):
    c4_container_diagram_path: str
    c4_component_diagram_path: str


class F4LangAgentState(AgentState):
    c4_component_diagram_path: str
    code_path: str


class RootState(TypedDict):
    user_input: str
    global_messages: Annotated[Sequence[BaseMessage], operator.add]
    c4_context_diagram_path: str
    c4_container_diagram_path: str
    c4_component_diagram_path: str
