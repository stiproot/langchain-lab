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
# from common.tools import MapYmlToJsonTool, RetrieveAdditionalContext
# from common.agent_factory import create_agent

os.environ["TAVILY_API_KEY"] = ""
tools = [TavilySearchResults(max_results=3)]

prompt = hub.pull("wfh/react-agent-executor")
prompt.pretty_print()

# Choose the LLM that will drive the agent
model = ModelFactory.create()
agent_executor = create_react_agent(model, tools=tools, messages_modifier=prompt)


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

# output = planner.invoke(
#     {
#         "messages": [
#             ("user", "what is the hometown of the current Australia open winner?")
#         ]
#     }
# )

# pprint.pprint(output)


replanner_prompt = ChatPromptTemplate.from_template(
    """
    For the given objective, come up with a simple step by step plan. \
    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

    Your objective was this:
    {input}

    Your original plan was this:
    {plan}

    You have currently done the follow steps:
    {past_steps}

    Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. 
    Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan.
    """
)


replanner_model = ModelFactory.create().with_structured_output(Act)
replanner = replanner_prompt | replanner_model


async def execute_step(state: PlanExecute):
    plan = state["plan"]
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    task_formatted = f"""
    For the following plan:
    {plan_str}\n\nYou are tasked with executing step {1}, {task}.
    """

    agent_response = await agent_executor.ainvoke(
        {"messages": [("user", task_formatted)]}
    )
    past_steps = agent_response["messages"][-1].content
    pprint.pprint(past_steps)
    return {
        "past_steps": (task, past_steps),
    }


async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    return {"plan": plan.steps}


async def replan_step(state: PlanExecute):
    output = await replanner.ainvoke(state)
    if isinstance(output.action, Response):
        return {"response": output.action.response}
    else:
        return {"plan": output.action.steps}


def should_end(state: PlanExecute) -> Literal["agent", "__end__"]:
    if "response" in state and state["response"]:
        return "__end__"
    else:
        return "agent"

workflow = StateGraph(PlanExecute)

# Add the plan node
workflow.add_node("planner", plan_step)

# Add the execution step
workflow.add_node("agent", execute_step)

# Add a replan node
workflow.add_node("replan", replan_step)

workflow.add_edge(START, "planner")

# From plan we go to agent
workflow.add_edge("planner", "agent")

# From agent, we replan
workflow.add_edge("agent", "replan")

workflow.add_conditional_edges(
    "replan",
    # Next, we pass in the function that will determine which node is called next.
    should_end,
)

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile()


async def run_workflow(app, inputs, config):
    async for event in app.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)

config = {"recursion_limit": 50}
inputs = {"input": "what is the hometown of the 2024 Australia open winner?"}

if __name__ == "__main__":
    asyncio.run(run_workflow(app, inputs, config))
