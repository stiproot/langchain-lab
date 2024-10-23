import pprint
import functools
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor
from common.utils.logger import log
from common.model_factory import ModelFactory
from common.tools import (
    write_contents_to_file,
    read_file_contents,
    RetrieveAdditionalContextTool,
    validate_mermaid_md,
    dotnet_build
)
from graphs.codegen.agents import (
    create_agent_executor,
    should_invoke_tools,
    invoke_tools,
)
from graphs.codegen.state import TaskTreeAgentState
from graphs.codegen.data_types import COLLECTION_NAMES
from graphs.codegen.prompts import TASK_TREE_PROMPT
from graphs.codegen.user_input import USER_INPUT


def init_state(state: TaskTreeAgentState):
    log(f"{init_state.__name__} START. state: {state}")

    user_input = state["user_input"]
    component_file_path = state["c4_component_diagram_path"]
    code_path = state["code_path"]

    content = f"""
        Input:
        C4 component diagram file path: {component_file_path}

        Output:
        Code path: {code_path}
    """

    state["messages"] += [HumanMessage(content=user_input), AIMessage(content=content)]

    log(f"{init_state.__name__} END. state: {state}")


def sync_state(state: TaskTreeAgentState):
    log(f"{sync_state.__name__} START.")

    state["global_messages"] += state["messages"][1:]

    log(f"{sync_state.__name__} END.")


def build_graph():

    context_retriever = RetrieveAdditionalContextTool(
        COLLECTION_NAMES.TASK_TREE_LIB.value
    )

    tools = [
        context_retriever,
        write_contents_to_file,
        read_file_contents,
        dotnet_build
    ]
    tool_executor = ToolExecutor(tools)

    prompt_text = TASK_TREE_PROMPT

    prompt = ChatPromptTemplate.from_messages(
        [("system", prompt_text), MessagesPlaceholder(variable_name="messages")]
    )

    model = ModelFactory.create().bind_tools(tools)
    chain = prompt | model

    graph = StateGraph(TaskTreeAgentState)

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
    inputs = {
        "messages": [HumanMessage(content=USER_INPUT)],
        "user_input": USER_INPUT,
        "c4_component_diagram_path": "/Users/simon.stipcich/code/repo/langchain-lab/graphs/codegen/.output/3.component-diag/10.2.c4-component-diagram.md",
        "code_path": "/Users/simon.stipcich/code/repo/langchain-lab/graphs/codegen/.output/4.task-tree/XxxAPI/",
    }

    for output in app.stream(inputs):
        for key, value in output.items():
            pprint.pprint(f"Output from node '{key}':")
            pprint.pprint("---")
            pprint.pprint(value, indent=2, width=80, depth=None)
        pprint.pprint("\n---\n")
