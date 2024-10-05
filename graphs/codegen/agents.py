import pprint
import logging
from langchain_core.runnables import Runnable
from graphs.codegen.state import AgentState
from graphs.codegen.logger import log


def create_agent_executor(chain: Runnable):
    def call_chain(state: AgentState):
        log("AGENT:")

        messages = state["messages"]
        log("MESSAGES:")
        pprint.pprint(messages)

        output = chain.invoke({"messages": messages})
        log("OUTPUT:")
        pprint.pprint(output)

        messages += [output]

    return call_chain
