import pprint
import os
import re
from functools import partial
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda, Runnable
from langchain_core.runnables.graph import Node
from langgraph.graph import START, END, StateGraph, Graph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation
from common.model_factory import ModelFactory
from common.agent_factory import create_agent
from common.tools import (
    write_contents_to_file,
    read_file_contents,
    RetrieveAdditionalContextTool,
    validate_mermaid_md,
)
from graphs.codegen.agents import (
    create_agent_executor,
    should_invoke_tools,
    invoke_tools,
)
from graphs.codegen.state import RootState
from graphs.codegen.c4_context_subgraph import build_graph as build_context_subgraph
from graphs.codegen.c4_container_subgraph import build_graph as build_container_subgraph
from graphs.codegen.c4_component_subgraph import build_graph as build_component_subgraph
from graphs.codegen.task_tree_subgraph import build_graph as build_task_tree_subgraph
from common.utils.logger import log
from graphs.codegen.data_types import COLLECTION_NAMES, C4_DIAGRAM_TYPES
from graphs.codegen.user_input import USER_INPUT


def init_state(state: RootState):
    log(f"{init_state.__name__} START.")

    folder_path = re.findall(r"`(/[^`]+/)`", state["user_input"])[0]

    state["c4_context_diagram_path"] = os.path.join(
        folder_path, f"{COLLECTION_NAMES.C4_SYSCONTEXT_DIAG.value}.md"
    )
    state["c4_container_diagram_path"] = os.path.join(
        folder_path, f"{COLLECTION_NAMES.C4_CONTAINER_DIAG.value}.md"
    )
    state["c4_component_diagram_path"] = os.path.join(
        folder_path, f"{COLLECTION_NAMES.C4_COMPONENT_DIAG.value}.md"
    )
    state["code_path"] = os.path.join(folder_path, "4.task-tree", "XxxAPI")

    log(f"{init_state.__name__} END.")

    return {
        "user_input": state["user_input"],
        "global_messages": state["global_messages"],
        "c4_context_diagram_path": state["c4_context_diagram_path"],
        "c4_container_diagram_path": state["c4_container_diagram_path"],
        "c4_component_diagram_path": state["c4_component_diagram_path"],
        "code_path": state["code_path"],
    }


def flush_state(state: RootState):
    log(f"{flush_state.__name__} START.")

    for msg in state["global_messages"]:
        log(msg.content)

    log(f"{flush_state.__name__} END.")


c4_context_subgraph = build_context_subgraph()
c4_container_subgraph = build_container_subgraph()
c4_component_subgraph = build_component_subgraph()
task_tree_subgraph = build_task_tree_subgraph()


root_builder = StateGraph(RootState)

root_builder.add_node("init_state", init_state)
root_builder.add_node("c4_context_diagram", c4_context_subgraph.compile())
root_builder.add_node("c4_container_diagram", c4_container_subgraph.compile())
root_builder.add_node("c4_component_diagram", c4_component_subgraph.compile())
root_builder.add_node("code", task_tree_subgraph.compile())
root_builder.add_node("flush_state", flush_state)

root_builder.add_edge(START, "init_state")
root_builder.add_edge("init_state", "c4_context_diagram")
root_builder.add_edge("c4_context_diagram", "c4_container_diagram")
root_builder.add_edge("c4_container_diagram", "c4_component_diagram")
root_builder.add_edge("c4_component_diagram", "code")
# root_builder.add_edge("c4_context_diagram", "flush_state")
# root_builder.add_edge("c4_container_diagram", "flush_state")
# root_builder.add_edge("c4_component_diagram", "flush_state")
root_builder.add_edge("code", "flush_state")
root_builder.add_edge("flush_state", END)

app = root_builder.compile()

inputs = {"messages": [HumanMessage(content=USER_INPUT)], "user_input": USER_INPUT}

for output in app.stream(inputs):
    for key, value in output.items():
        log(f"OUTPUT key: '{key}'\nvalue: {value}")
        # pprint.pprint("---")
        # pprint.pprint(value, indent=2, width=80, depth=None)
    # pprint.pprint("\n---\n")
