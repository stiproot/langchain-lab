import pprint
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
    RetrieveAdditionalContextTool,
    validate_mermaid_md,
)
from graphs.codegen.agents import (
    create_agent_executor,
    should_invoke_tools,
    invoke_tools,
)
from graphs.codegen.state import AgentState
from graphs.codegen.container_subgraph import build_graph

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
 
    Write the output to `/Users/simon.stipcich/code/repo/langchain-lab/graphs/codegen/.output/architecture.md`.
    """


def root_node_action(user_input):
    print("Entry node executed!")
    print(user_input)


root_graph = Graph()

# node = Node(
#     func=root_node_action,
#     name="root_entry",
#     inputs=["raw_data"],
#     outputs=["processed_data"],
# )

root_graph.add_node("root_entry", root_node_action)

sub_graph = build_graph().compile()

root_graph.add_node("container", sub_graph)

root_graph.add_edge(START, "root_entry")
root_graph.add_edge("root_entry", "container")
root_graph.add_edge("container", END)


app = root_graph.compile()

inputs = {"messages": [HumanMessage(content=user_input)]}

for output in app.stream(inputs):
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")
