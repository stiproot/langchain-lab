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
from langchain import hub
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor

from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.prebuilt.tool_executor import ToolExecutor

# This a helper class we have that is useful for running tools
# It takes in an agent action and calls that tool and returns the result

# from graphs.work_item_translation.supervisor.nodes import agent_node
# from graphs.work_item_translation.supervisor.supervisor import supervisor_chain, members
from common.model_factory import ModelFactory
from common.agent_factory import create_agent

# from common.prompts.sys_prompts import TXT_TO_YML_SYSP, YML_TO_JSON_SYSP
from common.tools import MapYmlToJsonTool, RetrieveAdditionalContext

# from common.agent_factory import create_agent

# model = ModelFactory.create()

map_yml_to_json_tool = MapYmlToJsonTool()
retriever_tool = RetrieveAdditionalContext()

tools = [retriever_tool]

tool_executor = ToolExecutor(tools)
# tool_node = ToolNode(tools)

user_input = (
    "Create a YAML work item tree structure out of the following text:\n"
    "<text>\n"
    "Build web application.\n"
    "Workflow builder web component.\n"
    "We need to investigate a database technology to use.\n"
    "Investigate Dapr workflows as a workflow engine.\n"
    "Build BFF (backend for frontend) API.\n"
    "</text>"
)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )


class Response(BaseModel):
    """Response to user."""

    response: str


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )


class AssignedStep(BaseModel):
    """The task, and entity to execute it."""

    step: str = Field(description="The step to execute.")

    entity: str = Field(description="The entity to execute out the step.")


class AssignedSteps(BaseModel):
    """A list of assigned steps."""

    assigned_steps: List[AssignedStep] = Field(description="A list of assigned steps.")


class StructuredYmlRes(BaseModel):
    """Structured YAML."""

    structured_yaml: str = Field(description="Structured YAML")


class WorkflowAgents(Enum):
    """Different agents in the workflow."""

    TRANSLATOR = "translator"
    ASSIGNER = "assigner"
    PLANNER = "planner"


class WorkflowTools(Enum):
    """Different tools in the workflow."""

    RETRIEVE_ADDITIONAL_CONTEXT = "retrieve_additional_context"


translator_prompt = """You are a helpful AI assistant. \
    Your job is to translate text to YAML. \
    The YAML needs to follow a specific structure. \
    Use to tools that are available to you to carry out the this task."""
translator_model = (
    ModelFactory.create().bind_tools(tools=[retriever_tool])
    # .with_structured_output(StructuredYmlRes)
)
translator_agent = create_agent(llm=translator_model, system_message=translator_prompt)


assigner_prompt = """Your job is to assign a step to an appropriate entity that can execute it. \
    An entity in this context could be a function, an agent or a tool. \
    The choice of entity should be chosen from the tools or agents provided to you."""
assigner_model = ModelFactory.create().with_structured_output(AssignedSteps)
assigner_agent = create_agent(llm=assigner_model, system_message=assigner_prompt)


planner_prompt = f"""For the given objective, come up with a step by step plan. \
    Use the tools available to you to complete your plan. \
    This plan should involve individual tasks. \
    Make sure that each step has all the information needed. \
    Tools: {WorkflowTools.RETRIEVE_ADDITIONAL_CONTEXT.value}, Agents: {WorkflowAgents.ASSIGNER.value}, {WorkflowAgents.TRANSLATOR.value}"""
planner_model = ModelFactory.create().with_structured_output(Plan)
planner_agent = create_agent(llm=planner_model, system_message=planner_prompt)


def create_planner_agent_executor(chain):
    def call_chain(state: AgentState):
        pprint.pprint("MESSAGES:")
        messages = state["messages"]
        pprint.pprint(messages)

        output = chain.invoke({"messages": messages})
        pprint.pprint("OUTPUT:")
        pprint.pprint(output)

        message = "\n".join([f"Step {i+1}: {s}" for i, s in enumerate(output.steps)])
        pprint.pprint("MESSAGE:")
        pprint.pprint(message)

        messages += [AIMessage(content=message, tools=[])]

    return call_chain


def create_assigner_agent_executor(chain):
    def call_chain(state: AgentState):
        messages = state["messages"]
        pprint.pprint(messages)

        output = chain.invoke({"messages": messages})
        pprint.pprint(output)

        message = "\n".join(
            [
                f"{i+1}. Assigned: {s.entity} -> Step: {s.step}"
                for i, s in enumerate(output.assigned_steps)
            ]
        )
        pprint.pprint("MESSAGE:")
        pprint.pprint(message)

        messages += [AIMessage(content=message, tools=[])]

    return call_chain


def create_translator_agent_executor(chain):
    def call_chain(state: AgentState):
        messages = state["messages"]
        pprint.pprint(messages)

        output = chain.invoke({"messages": messages})
        pprint.pprint(output)

        messages += output

    return call_chain


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

    if isinstance(messages[-1], ToolMessage):
        return "call_tool"
    else:
        return "continue"


workflow = StateGraph(AgentState)

planner_node = create_planner_agent_executor(planner_agent)
workflow.add_node("planner", planner_node)

assigner_node = create_assigner_agent_executor(assigner_agent)
workflow.add_node("assigner", assigner_node)

translator_node = create_translator_agent_executor(translator_agent)
workflow.add_node("translator", translator_node)

workflow.add_node("call_tool", call_tool)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "assigner")
workflow.add_edge("assigner", "translator")

# workflow.add_edge("assigner", END)

workflow.add_conditional_edges(
    "translator",
    should_use_tool,
    {
        "call_tool": "call_tool",
        "continue": END,
    },
)

app = workflow.compile()

inputs = {"messages": [HumanMessage(content=user_input)]}
for output in app.stream(inputs):
    # stream() yields dictionaries with output keyed by node name
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")
