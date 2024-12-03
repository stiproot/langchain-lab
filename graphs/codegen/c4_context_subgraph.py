import pprint
import functools
import chromadb
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor

from agnt_smth.core.utls import log, ModelFactory, ChromaHttpClientFactory, EmbeddingFactory, RetrieverFactory
from agnt_smth.core.tools import (
    write_contents_to_file,
    read_file_contents,
    RetrieveAdditionalContextTool,
    validate_mermaid_md,
)
from agnt_smth.core.agnts import (
    create_agent_executor,
    should_invoke_tools,
    invoke_tools,
)

from graphs.codegen.state import C4ContextAgentState
from graphs.codegen.data_types import COLLECTION_NAMES, C4_DIAGRAM_TYPES
from graphs.codegen.prompts import C4_CONTEXT_PROMPT_TEMPLATE


def init_state(state: C4ContextAgentState):
    log(f"{init_state.__name__} START.")

    user_input = state["user_input"]
    context_file_path = state["c4_context_diagram_path"]

    content = f"""
        Output:
        C4 context diagram file path: {context_file_path}
    """

    state["messages"] += [HumanMessage(content=user_input), AIMessage(content=content)]

    log(f"{init_state.__name__} END.")


def sync_state(state: C4ContextAgentState):
    log(f"{sync_state.__name__} START.")

    state["global_messages"] += state["messages"][1:]

    log(f"{sync_state.__name__} END.")


def build_graph():

    chroma_client = ChromaHttpClientFactory.create_with_auth()
    embedding_function = EmbeddingFactory.create()
    retriever = RetrieverFactory.create(COLLECTION_NAMES.C4_SYSCONTEXT_DIAG.value, chroma_client=chroma_client, embedding_function=embedding_function)

    context_retriever = RetrieveAdditionalContextTool(retriever)

    tools = [context_retriever, write_contents_to_file, validate_mermaid_md]
    tool_executor = ToolExecutor(tools)

    prompt_text = C4_CONTEXT_PROMPT_TEMPLATE.replace(
        "{{c4-diagram-type}}", C4_DIAGRAM_TYPES.C4_SYSCONTEXT_DIAG.value
    ).replace("{{c4-collection-type}}", COLLECTION_NAMES.C4_SYSCONTEXT_DIAG.value)

    prompt = ChatPromptTemplate.from_messages(
        [("system", prompt_text), MessagesPlaceholder(variable_name="messages")]
    )

    model = ModelFactory.create().bind_tools(tools)
    chain = prompt | model

    graph = StateGraph(C4ContextAgentState)

    agent_node = create_agent_executor(chain=chain)

    graph.add_node("init_state", init_state)
    graph.add_node("agent", agent_node)
    graph.add_node(
        "invoke_tools", functools.partial(invoke_tools, tool_executor=tool_executor)
    )
    graph.add_node("sync_state", sync_state)

    graph.add_edge(START, "init_state")
    graph.add_edge("init_state", "agent")

    graph.add_conditional_edges(
        "agent",
        should_invoke_tools,
        {
            "invoke_tools": "invoke_tools",
            "continue": "sync_state",
        },
    )

    graph.add_edge("invoke_tools", "agent")
    graph.add_edge("agent", "sync_state")
    graph.add_edge("sync_state", END)

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
