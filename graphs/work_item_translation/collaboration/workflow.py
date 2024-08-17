import functools
import operator
import pprint
from typing import Sequence, TypedDict, Annotated, Literal

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from graphs.work_item_translation.supervisor.nodes import agent_node
from graphs.work_item_translation.supervisor.supervisor import supervisor_chain, members

from common.model_factory import ModelFactory
from common.prompts.sys_prompts import TXT_TO_YML_SYSP, YML_TO_JSON_SYSP
from common.tools import MapYmlToJsonTool, RetrieveAdditionalContext
from common.agent_factory import create_agent


def router(state) -> Literal["call_tool", "__end__", "continue"]:
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        # The previous agent is invoking a tool
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return "__end__"
    return "continue"


# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str

map_yml_to_json_tool = MapYmlToJsonTool()
retriever_tool = RetrieveAdditionalContext()

tools = [map_yml_to_json_tool, retriever_tool]
tool_node = ToolNode(tools)


agent_llm_1 = ModelFactory.create()
txt_to_yml_agent = create_agent(agent_llm_1, [retriever_tool], TXT_TO_YML_SYSP)
txt_to_yml_node = functools.partial(
    agent_node, agent=txt_to_yml_agent, name="txt_to_yml"
)

agent_llm_2 = ModelFactory.create()
yml_to_json_agent = create_agent(agent_llm_2, [map_yml_to_json_tool], YML_TO_JSON_SYSP)
yml_to_json_node = functools.partial(
    agent_node, agent=yml_to_json_agent, name="yml_to_json"
)

workflow = StateGraph(AgentState)
workflow.add_node("txt_to_yml", txt_to_yml_node)
workflow.add_node("yml_to_json", yml_to_json_node)
workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "txt_to_yml", 
    router,
    {"continue": "yml_to_json", "call_tool": "call_tool", "__end__": END}
)
workflow.add_conditional_edges(
    "yml_to_json", 
    router,
    {"continue": "txt_to_yml", "call_tool": "call_tool", "__end__": END}
)
workflow.add_conditional_edges(
    "call_tool",
    lambda state: state["sender"],
    {
        "txt_to_yml": "txt_to_yml",
        "yml_to_json": "yml_to_json",
    }
)


workflow.add_edge(START, "txt_to_yml")

graph = workflow.compile()

user_input = (
    "Create a work item tree structure as YAML out of the following text:\n"
    "Build web application.\n"
    "Workflow builder web component.\n"
    "We need to investigate a database technology to use.\n"
    "Investigate Dapr workflows as a workflow engine.\n"
    "Build BFF (backend for frontend) API."
)

for output in graph.stream(
    {
        "messages": [
            HumanMessage(
                content="Please translate the following TEXT to JSON.\n" + user_input
            )
        ]
    },
    {"recursion_limit": 100},
):
    # if "__end__" not in s:
    #     print(s)
    #     print("----")
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")

# for output in graph.stream(inputs):
#     for key, value in output.items():
#         pprint.pprint(f"Output from node '{key}':")
#         pprint.pprint("---")
#         pprint.pprint(value, indent=2, width=80, depth=None)
#     pprint.pprint("\n---\n")
