import os
import bs4
import json
from typing import Annotated, Literal
from typing_extensions import TypedDict

from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import ToolMessage, AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition

from common.config_loader import load_openai_config
from chromadb import Client


def get_data():
    with open(".data/wis.md") as f:
        content = f.read()
        return content


memory = SqliteSaver.from_conn_string(":memory:")

openai_config = load_openai_config()


loader = TextLoader(".data/wis.md")
docs = loader.load()

# ---------------

# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# docs = text_splitter.split_documents(documents)
# embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# db = Chroma.from_documents(docs, embedding_function, persist_directory=".db/chroma_db")

# retriever = VectorStoreRetriever(vector_store=db)

# ---------------
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, chunk_overlap=50
)
doc_splits = text_splitter.split_documents(docs)

vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="work-item-hierarchy-example",
    embedding=AzureOpenAIEmbeddings(),
    persist_directory=".db/chroma_db",
)
retriever = vectorstore.as_retriever()

# ---------------


@tool
def query_vector_store(query: str) -> str:
    """Queries a vector store for additional information."""
    return retriever.retrieve(query)


tools = [query_vector_store]

llm = AzureChatOpenAI(**openai_config)
llm_with_tools = llm.bind_tools(tools)

system_prompt = (
    "You are work item translator assistant. "
    "You translate raw text into a logical work item tree structure in YAML format. "
    "Use the vector store function to retrieve examples of what the work item tree structure should look like. "
    "Your output should only consist of YAML formatted text."
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent(state: State):
    return {"messages": llm_with_tools.invoke(state["messages"])}


tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)

graph_builder.add_node("agent", agent)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges(
    "agent",
    tools_condition,
)
graph_builder.add_edge("tools", "agent")
graph_builder.add_edge(START, "agent")
graph_builder.add_edge("agent", END)

graph = graph_builder.compile(
    checkpointer=memory,
)


config = {"configurable": {"thread_id": "1"}}
user_input = (
    "Build web application."
    "Workflow builder web component."
    "We need to investigate a database technology to use."
    "Investigate Dapr workflows as a workflow engine."
    "Build BFF (backend for frontend) API."
)

events = graph.stream(
    {"messages": [("user", user_input)]}, config, stream_mode="values"
)
for event in events:
    event["messages"][-1].pretty_print()
