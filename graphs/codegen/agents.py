from typing import List, Any, Optional
import pprint
import logging
from langchain_core.runnables import Runnable
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation
from graphs.codegen.state import AgentState
from common.utils.logger import log


def create_agent_executor(chain: Runnable, messages_key: Optional[str] = "messages"):
    def invoke_chain(state: AgentState):
        log(f"{invoke_chain.__name__} START.")

        messages = state[messages_key]
        # log("MESSAGES:")
        # pprint.pprint(messages)

        output = chain.invoke({"messages": messages})
        # log("OUTPUT:")
        # pprint.pprint(output)

        messages += [output]
        log(f"{invoke_chain.__name__} END.")

    return invoke_chain


def should_invoke_tools(state: AgentState):
    log(f"{should_invoke_tools.__name__} START.")

    messages = state["messages"]
    # log("MESSAGES:")
    # pprint.pprint(messages)

    last_message = messages[-1]
    # log("LAST MESSAGE:")
    # pprint.pprint(last_message)

    log(f"{should_invoke_tools.__name__} END.")

    if last_message.tool_calls:
        return "invoke_tools"

    return "continue"


def invoke_tools(state: AgentState, tool_executor):
    log(f"{invoke_tools.__name__} START.")

    messages = state["messages"]
    # log("MESSAGES:")
    # pprint.pprint(messages)

    last_message = messages[-1]
    tool_invocations = []

    for tool_call in last_message.tool_calls:
        action = ToolInvocation(
            tool=tool_call["name"],
            tool_input=tool_call["args"],
        )
        tool_invocations.append(action)

    responses = tool_executor.batch(tool_invocations, return_exceptions=True)

    tool_messages = [
        ToolMessage(
            content=str(response),
            name=tc["name"],
            tool_call_id=tc["id"],
        )
        for tc, response in zip(last_message.tool_calls, responses)
    ]

    log(f"{invoke_tools.__name__} END.")

    return {"messages": tool_messages}
