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
from common.utils.logger import log
from graphs.codegen.data_types import C4_COLLECTIONS, C4_DIAGRAM_TYPES

user_input = """
    Use case:
    As as user, I would like to translate a meeting transcript into Azure DevOps Work Items.
    I would like to upload the transcript to a web application, and have it build a work item hierarchy.
    If I approve the hierarchy, I would like the web application to create the work items in Azure DevOps.

    Technical requirements:
    - The system should be able to handle 1000 requests per second.
    - The system should be able to store 1TB of data.
    - The system should use a NoSQL database.
    - The system should be able to scale horizontally.
    - The system should use Dapr for microservices.
    - Vue.js should be used for the frontend.
    - Python should be used for the backend.
 
    Write the output to the following folder `/Users/simon.stipcich/code/repo/langchain-lab/graphs/codegen/.output/`.
    """


def init_state(state: RootState):
    log(f"{init_state.__name__} START.")

    folder_path = re.findall(r"`(/[^`]+/)`", state["user_input"])[0]

    state["c4_context_diagram_path"] = os.path.join(
        folder_path, f"{C4_COLLECTIONS.CONTEXT.value}.md"
    )
    state["c4_container_diagram_path"] = os.path.join(
        folder_path, f"{C4_COLLECTIONS.CONTAINER.value}.md"
    )

    log(f"{init_state.__name__} END.")

    return {
        "c4_context_diagram_path": state["c4_context_diagram_path"],
        "c4_container_diagram_path": state["c4_container_diagram_path"],
        "messages": state["messages"],
        "user_input": state["user_input"],
    }


def flush_state(state: RootState):
    log(f"{flush_state.__name__} START.")

    for msg in state["messages"]:
        log(msg.content)

    log(f"{flush_state.__name__} END.")


c4_context_subgraph = build_context_subgraph()
# c4_container_subgraph = build_container_subgraph()

root_builder = StateGraph(RootState)

root_builder.add_node("init_state", init_state)
root_builder.add_node("flush_state", flush_state)
root_builder.add_node("c4_context_diagram", c4_context_subgraph.compile())
# root_builder.add_node("c4_container_diagram", c4_container_subgraph.compile())

root_builder.add_edge(START, "init_state")
root_builder.add_edge("init_state", "c4_context_diagram")
# root_builder.add_edge("c4_context_diagram", "c4_container_diagram")
# root_builder.add_edge("c4_container_diagram", END)
root_builder.add_edge("c4_context_diagram", "flush_state")
root_builder.add_edge("flush_state", END)

app = root_builder.compile()

inputs = {"messages": [HumanMessage(content=user_input)], "user_input": user_input}

for output in app.stream(inputs):
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")
