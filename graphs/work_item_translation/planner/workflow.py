import functools
import operator
import pprint
import asyncio
import os
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

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain import hub
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor

from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode, create_react_agent

# from graphs.work_item_translation.supervisor.nodes import agent_node
# from graphs.work_item_translation.supervisor.supervisor import supervisor_chain, members
from common.model_factory import ModelFactory

# from common.prompts.sys_prompts import TXT_TO_YML_SYSP, YML_TO_JSON_SYSP
from common.tools import MapYmlToJsonTool, RetrieveAdditionalContext

# from common.agent_factory import create_agent

# model = ModelFactory.create()

map_yml_to_json_tool = MapYmlToJsonTool()
retriever_tool = RetrieveAdditionalContext()

tools = [map_yml_to_json_tool, retriever_tool]
# tool_node = ToolNode(tools)

user_input = (
    "Create a work item tree structure as YAML out of the following text:\n"
    "Build web application.\n"
    "Workflow builder web component.\n"
    "We need to investigate a database technology to use.\n"
    "Investigate Dapr workflows as a workflow engine.\n"
    "Build BFF (backend for frontend) API."
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


planner_prompt = """For the given objective, come up with a simple step by step plan. \
    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps."""

planner_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            planner_prompt,
        ),
        ("placeholder", "{messages}"),
    ]
)
planner_model = ModelFactory.create().with_structured_output(Plan)
planner_chain = planner_prompt_template | planner_model

assigner_prompt = """Your job is to assign a step to the appropraite entity that can execute it. An entity in this context could be a function, an agent or a tool."""
assigner_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            assigner_prompt,
        ),
        ("placeholder", "{messages}"),
    ]
)
assigner_model = ModelFactory.create().with_structured_output(AssignedSteps)
assigner_chain = assigner_prompt_template | assigner_model


def create_chain(llm: AzureChatOpenAI, system_message: str, tools: list = []):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    # prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    # return prompt | llm.bind_tools(tools)
    return prompt | llm


def create_planner_chain_executor(chain):
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


def create_assigner_chain_executor(chain):
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


def call_tool(state):
    messages = state["messages"]
    # Based on the continue condition
    # we know the last message involves a function call
    last_message = messages[-1]
    # We construct an ToolInvocation for each tool call
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


# def should_continue(state):
#     messages = state["messages"]
#     last_message = messages[-1]
#     # If there is no function call, then we finish
#     if not last_message.tool_calls:
#         return "end"
#     # Otherwise if there is, we continue
#     else:
#         return "continue"

workflow = StateGraph(AgentState)

# workflow.add_node("planner", planner_chain)
# planner_chain = create_chain(planner_model, planner_prompt)
# planner_agent_executor = AgentExecutor(agent=planner_agent, handle_parsing_errors=True)
planner_agent = create_planner_chain_executor(planner_chain)
workflow.add_node("planner", planner_agent)

# workflow.add_node("assigner", assigner_chain)
assigner_agent = create_assigner_chain_executor(assigner_chain)
# assigner_agent_executor = AgentExecutor(agent=assigner_agent, handle_parsing_errors=True)
workflow.add_node("assigner", assigner_agent)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "assigner")
workflow.add_edge("assigner", END)

# # We now add a conditional edge
# workflow.add_conditional_edges(
#     # First, we define the start node. We use `agent`.
#     # This means these are the edges taken after the `agent` node is called.
#     "agent",
#     # Next, we pass in the function that will determine which node is called next.
#     should_continue,
#     # Finally we pass in a mapping.
#     # The keys are strings, and the values are other nodes.
#     # END is a special node marking that the graph should finish.
#     # What will happen is we will call `should_continue`, and then the output of that
#     # will be matched against the keys in this mapping.
#     # Based on which one it matches, that node will then be called.
#     {
#         # If `tools`, then we call the tool node.
#         "continue": "action",
#         # Otherwise we finish.
#         "end": END,
#     },
# )
#
# # We now add a normal edge from `tools` to `agent`.
# # This means that after `tools` is called, `agent` node is called next.
# workflow.add_edge("action", "agent")
#
# # Finally, we compile it!
# # This compiles it into a LangChain Runnable,
# # meaning you can use it as you would any other runnable
app = workflow.compile()

inputs = {"messages": [HumanMessage(content=user_input)]}
for output in app.stream(inputs):
    # stream() yields dictionaries with output keyed by node name
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")
