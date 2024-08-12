from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
import pprint

from graphs.work_item_translator.agent_state import AgentState
from graphs.work_item_translator.agent_node import agent
from graphs.work_item_translator.generate_node import generate
from graphs.work_item_translator.retriever_factory import tools
from graphs.work_item_translator.rewrite_node import rewrite
from graphs.work_item_translator.validate_edge import validate_documents

# Define a new graph
workflow = StateGraph(AgentState)

# Define the nodes we will cycle between
workflow.add_node("agent", agent)  # agent
retrieve = ToolNode(tools)
workflow.add_node("retrieve", retrieve)  # retrieval
workflow.add_node("rewrite", rewrite)  # Re-writing the question
workflow.add_node(
    "generate", generate
)  # Generating a response after we know the documents are relevant
# Call agent node to decide to retrieve or not
workflow.add_edge(START, "agent")

# Decide whether to retrieve
workflow.add_conditional_edges(
    "agent",
    # Assess agent decision
    tools_condition,
    {
        # Translate the condition outputs to nodes in our graph
        "tools": "retrieve",
        END: END,
    },
)

# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    validate_documents,
)
workflow.add_edge("generate", END)
workflow.add_edge("rewrite", "agent")

# Compile
graph = workflow.compile()

user_input = (
    "Create a work item tree structure as YAML out of the following text:\n"
    "Build web application."
    "Workflow builder web component."
    "We need to investigate a database technology to use."
    "Investigate Dapr workflows as a workflow engine."
    "Build BFF (backend for frontend) API."
)

inputs = {
    "messages": [
        ("user", user_input),
    ]
}
for output in graph.stream(inputs):
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")
