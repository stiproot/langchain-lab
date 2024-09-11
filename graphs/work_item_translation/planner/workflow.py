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

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda
from langchain import hub
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor

from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation

from common.model_factory import ModelFactory
from common.agent_factory import create_agent

from common.tools import MapYmlToJsonTool, RetrieveAdditionalContextTool

map_yml_to_json_tool = MapYmlToJsonTool()
retriever_tool = RetrieveAdditionalContextTool()

tools = [retriever_tool]

tool_executor = ToolExecutor(tools)

user_input = (
    "Translate the following text into YAML:\n"
    "<text>\n"
    "Build web application.\n"
    "Workflow builder web component.\n"
    "We need to investigate a database technology to use.\n"
    "Investigate Dapr workflows as a workflow engine.\n"
    "Build BFF (backend for frontend) API.\n"
    "</text>"
)


class Step(BaseModel):
    """A step to carry out, along with the entity to carry it out."""

    step_number: int = Field(description="The number of the step in the plan.")
    step_definition: str = Field(description="A description of the step.")
    step_agent: str = Field(
        description="The agent responsible for carrying out the step."
    )
    status: str = Field(
        description="The status of the step, can be 'completed', 'in progress', 'not started'"
    )


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[Step] = Field(
        description="different steps of a plan to follow, should be in sorted order"
    )


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    steps: Annotated[Sequence[Step], operator.add]


translator_prompt = f"""You are a helpful AI assistant. \
    Your job is to translate text to YAML. \
    The YAML needs to follow a specific structure, use the {retriever_tool.name} to find an example of the structure. \
    """
translator_model = ModelFactory.create().bind_tools(tools=[retriever_tool])
translator_agent = create_agent(
    llm=translator_model, system_message=translator_prompt, tools=[retriever_tool]
)

planner_prompt = f"""Translate a user request into a plan to execute. \
    Each step consists of a description and the agent responsible for executing the step. \
    IMPORTANT: you an only choose agents from a list provided to you. \
    AGENTS AVAILABLE: text_to_yml_translator_agent"""
planner_model = ModelFactory.create().with_structured_output(Plan)
planner_agent = create_agent(llm=planner_model, system_message=planner_prompt)


def create_planner_agent_executor(chain):
    def call_chain(state: AgentState):
        print("PLANNER:")

        messages = state["messages"]
        print("MESSAGES:")
        pprint.pprint(messages)

        output = chain.invoke({"messages": messages})
        print("OUTPUT:")
        pprint.pprint(output)

        state["steps"] = output

        message = "\n".join([f"Step {i+1}: {s}\n" for i, s in enumerate(output.steps)])
        messages += [AIMessage(content=message, tools=[])]

        print("MESSAGE:")
        pprint.pprint(message)

    return call_chain


def create_translator_agent_executor(chain):
    def call_chain(state: AgentState):
        pprint.pprint("TRANSLATOR:")

        messages = state["messages"]
        pprint.pprint("MESSAGES:")
        pprint.pprint(messages)

        output = chain.invoke({"messages": messages})
        pprint.pprint("OUTPUT:")
        pprint.pprint(output)

        messages += [output]

    return call_chain


def handle_tool_error(state: AgentState) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def call_tool(state):
    pprint.pprint("CALL_TOOL:")

    messages = state["messages"]
    pprint.pprint("MESSAGES:")
    pprint.pprint(messages)

    last_message = messages[-1]
    tool_invocations = []

    for tool_call in last_message.tool_calls:
        action = ToolInvocation(
            tool=tool_call["name"],
            tool_input=tool_call["args"],
        )
        tool_invocations.append(action)

    action = ToolInvocation(
        tool=tool_call["name"],
        tool_input=tool_call["args"],
    )
    # We call the tool_executor and get back a response
    responses = tool_executor.batch(tool_invocations, return_exceptions=True)
    # We use the response to create tool messages
    tool_messages = [
        ToolMessage(
            content=str(response),
            name=tc["name"],
            tool_call_id=tc["id"],
        )
        for tc, response in zip(last_message.tool_calls, responses)
    ]

    # We return a list, because this will get added to the existing list
    return {"messages": tool_messages}


def should_use_tool(state):
    pprint.pprint("SHOULD_USE_TOOL:")

    messages = state["messages"]
    pprint.pprint("MESSAGES:")
    pprint.pprint(messages)

    last_message = messages[-1]
    pprint.pprint("LAST MESSAGE:")
    pprint.pprint(last_message)

    if last_message.tool_calls:
        return "call_tool"

    return "continue"


workflow = StateGraph(AgentState)

planner_node = create_planner_agent_executor(planner_agent)
workflow.add_node("planner", planner_node)

# translator_node = create_translator_agent_executor(translator_agent)
# workflow.add_node("translator", translator_node)

# workflow.add_node("call_tool", create_tool_node_with_fallback(tools))

workflow.add_edge(START, "planner")
workflow.add_edge("planner", END)

# workflow.add_conditional_edges(
#     "translator",
#     should_use_tool,
#     {
#         "call_tool": "call_tool",
#         "continue": END,
#     },
# )

app = workflow.compile()

inputs = {"messages": [HumanMessage(content=user_input)]}
for output in app.stream(inputs):
    # stream() yields dictionaries with output keyed by node name
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")
