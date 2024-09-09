import functools
import operator
import pprint
import asyncio
import os
from enum import Enum
from typing import (
    Sequence,
    TypedDict,
    Annotated,
    Literal,
    Annotated,
    List,
    Tuple,
    Union,
)

from langchain_openai import AzureChatOpenAI

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda
from langchain import hub
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor

from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.prebuilt.tool_executor import ToolExecutor

from common.model_factory import ModelFactory
from common.agent_factory import create_agent

from common.tools import write_contents_to_file


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
 
    Write the output to `/Users/simon.stipcich/code/repo/langchain-lab/graphs/codegen/architecture.md`.
    """


uml_prompt = f"""
    You are a UML design agent with expertise in creating C4 component diagrams using Mermaid syntax. Your primary task is to assist in designing software architectures by generating C4 component diagrams that visually represent systems, subsystems, components, and their relationships. You should follow these guidelines:

    Understand the Requirements: Ask for any missing details necessary to create an accurate C4 component diagram, such as the context, components, their interactions, and any external systems involved.

    Use Mermaid Syntax: Generate the diagrams using Mermaid syntax, ensuring that the structure follows C4 model principles (Context, Container, Component, and Code diagrams).

    Focus on Clarity and Accuracy: Ensure that the diagrams are clear, concise, and easy to understand, accurately representing the architectural components and their relationships.

    Provide Explanations: Along with the diagram, provide a brief explanation of the components, their purpose, and their interactions.

    Iterate Based on Feedback: If revisions are needed, ask for specific feedback and modify the diagrams accordingly.

    You are a helpful, knowledgeable assistant for anyone seeking to understand and visualize software architectures through C4 component diagrams.

    Write C4 diagram to a file when you are finished, using the tool provided.
    """

prompt = ChatPromptTemplate.from_messages(
    [("system", uml_prompt), ("human", "{user_input}")]
)

model = ModelFactory.create().bind_tools([write_contents_to_file])
chain = prompt | model

output = chain.invoke({"user_input": user_input})
pprint.pprint(output)

tool_calls = output.tool_calls
tool_name_mapping = {tool.name: tool for tool in [write_contents_to_file]}
tool_outputs = []

for tool_call in tool_calls:
    tool_outputs.append(tool_name_mapping[tool_call["name"]].invoke(tool_call["args"]))
pprint.pprint(tool_outputs)
