import pprint
import functools
import operator
from typing import TypedDict, Sequence, Annotated

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor

from agnt_smth.core.utls import log, ModelFactory, ChromaHttpClientFactory, EmbeddingFactory, RetrieverFactory
from agnt_smth.core.tools import RetrieveAdditionalContextTool
from agnt_smth.core.agnts import (
    create_agent_executor,
    should_invoke_tools,
    invoke_tools,
    AgentState,
)

SYS_PROMPT = """
    You are a helpful agent with expertise in answering technical questions about a code repository.

    You should follow these guidelines:
    - Understand the Requirements: use the context retriever tool to look up the necessary information about the repository. You can use the context retriever tool as many times as you need to gather the necessary information.
    - Focus on Clarity and Accuracy: Ensure that the answer is clear, concise, and easy to understand, and accurate.
    - Formulate a Response: Format a response that addresses the question and provides the necessary information.
"""


def build_graph(repo_name: str):

    chroma_client = ChromaHttpClientFactory.create_with_auth()
    embedding_function = EmbeddingFactory.create()
    retriever = RetrieverFactory.create(collection_name=repo_name, chroma_client=chroma_client, embedding_function=embedding_function)
    context_retriever = RetrieveAdditionalContextTool(repo_name, retriever=retriever)

    tools = [context_retriever]
    tool_executor = ToolExecutor(tools)

    prompt = ChatPromptTemplate.from_messages(
        [("system", SYS_PROMPT), MessagesPlaceholder(variable_name="messages")]
    )

    model = ModelFactory.create().bind_tools(tools)
    chain = prompt | model
    agent_node = create_agent_executor(chain=chain)

    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node(
        "invoke_tools", functools.partial(invoke_tools, tool_executor=tool_executor)
    )

    graph.add_edge(START, "agent")

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

    return graph.compile()


if __name__ == "__main__":
    repo_name = "Internal-Lexi"

    graph = build_graph(repo_name)

    inputs = {
        "messages": [HumanMessage(content=USER_INPUT)],
        "user_input": "What can you tell me about Lexi?",
    }

    for output in app.stream(inputs):
        for key, value in output.items():
            pprint.pprint(f"Output from node '{key}':")
            pprint.pprint("---")
            pprint.pprint(value, indent=2, width=80, depth=None)
        pprint.pprint("\n---\n")
