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
from agnt_smth.core.agnts import AgentState
from agnt_smth.core.workflows import build_agnt_with_tools_graph

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
    retriever = RetrieverFactory.create(repo_name, chroma_client=chroma_client, embedding_function=embedding_function)
    print("retriever type", type(retriever))
    context_retriever = RetrieveAdditionalContextTool(retriever, collection_name=repo_name)

    tools = [context_retriever]

    graph = build_agnt_with_tools_graph(sys_prompt=SYS_PROMPT, tools=tools)

    return graph



if __name__ == "__main__":

    repo_name = "Internal-Lexi"
    inputs = {"messages": [HumanMessage(content="What is Lexi? How can I run it?")]}

    app = build_graph(repo_name)

    for output in app.stream(inputs):
        for key, value in output.items():
            pprint.pprint(f"Output from node '{key}':")
            pprint.pprint("---")
            pprint.pprint(value, indent=2, width=80, depth=None)
        pprint.pprint("\n---\n")
