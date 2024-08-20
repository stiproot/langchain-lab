import functools
import operator
import pprint
import asyncio
import os
from typing import Sequence, TypedDict, Annotated, Literal, Annotated, List, Tuple, Union

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain import hub
from langchain_community.tools.tavily_search import TavilySearchResults


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
tool_node = ToolNode(tools)

user_input = (
    "Create a work item tree structure as YAML out of the following text:\n"
    "Build web application.\n"
    "Workflow builder web component.\n"
    "We need to investigate a database technology to use.\n"
    "Investigate Dapr workflows as a workflow engine.\n"
    "Build BFF (backend for frontend) API."
)


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


planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.""",
        ),
        ("placeholder", "{messages}"),
    ]
)

planner_model = ModelFactory.create().with_structured_output(Plan)
planner = planner_prompt | planner_model

output = planner.invoke(
    {
        "messages": [
            ("user", user_input)
        ]
    }
)

pprint.pprint(output)
