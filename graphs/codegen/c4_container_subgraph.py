import pprint
import functools
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda, Runnable
from langgraph.graph import START, END, StateGraph
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
from graphs.codegen.state import C4ContainerAgentState
from graphs.codegen.data_types import C4_COLLECTIONS, C4_DIAGRAM_TYPES
from graphs.codegen.prompts import C4_CONTAINER_PROMPT_TEMPLATE
from common.utils.logger import log


def init_state(state: C4ContainerAgentState):
    log(f"{init_state.__name__} START. state: {state}")

    user_input = state["user_input"]
    context_file_path = state["c4_context_diagram_path"]
    container_file_path = state["c4_container_diagram_path"]

    content = f"""
        Input:
        C4 context diagram file path: {context_file_path}

        Output:
        C4 container diagram file path: {container_file_path}
    """

    state["messages"] += [HumanMessage(content=user_input), AIMessage(content=content)]

    log(f"{init_state.__name__} END. state: {state}")


def sync_state(state: C4ContainerAgentState):
    log(f"{sync_state.__name__} START.")

    state["global_messages"] += state["messages"]

    log(f"{sync_state.__name__} END.")


def build_graph():

    context_retriever = RetrieveAdditionalContextTool(C4_COLLECTIONS.CONTAINER.value)

    tools = [
        context_retriever,
        write_contents_to_file,
        read_file_contents,
        validate_mermaid_md,
    ]
    tool_executor = ToolExecutor(tools)

    prompt_text = C4_CONTAINER_PROMPT_TEMPLATE.replace(
        "{{c4-diagram-type}}", C4_DIAGRAM_TYPES.CONTAINER.value
    ).replace("{{c4-collection-type}}", C4_COLLECTIONS.CONTAINER.value)

    prompt = ChatPromptTemplate.from_messages(
        [("system", prompt_text), MessagesPlaceholder(variable_name="messages")]
    )

    model = ModelFactory.create().bind_tools(tools)
    chain = prompt | model

    graph = StateGraph(C4ContainerAgentState)

    agent_node = create_agent_executor(chain=chain)

    graph.add_node("init_state", init_state)
    graph.add_node("agent", agent_node)
    graph.add_node(
        "invoke_tools", functools.partial(invoke_tools, tool_executor=tool_executor)
    )

    graph.add_edge(START, "init_state")
    graph.add_edge("init_state", "agent")

    graph.add_conditional_edges(
        "agent",
        should_invoke_tools,
        {
            "invoke_tools": "invoke_tools",
            "continue": END,
        },
    )

    graph.add_edge("invoke_tools", "agent")
    graph.add_edge("agent", END)

    return graph


if __name__ == "__main__":
    graph = build_graph()
    app = graph.compile()
    inputs = {"messages": [HumanMessage(content=user_input)]}

    for output in app.stream(inputs):
        for key, value in output.items():
            pprint.pprint(f"Output from node '{key}':")
            pprint.pprint("---")
            pprint.pprint(value, indent=2, width=80, depth=None)
        pprint.pprint("\n---\n")
