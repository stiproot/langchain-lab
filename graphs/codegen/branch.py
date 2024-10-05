import pprint
from functools import partial
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda, Runnable
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation
from common.model_factory import ModelFactory
from common.agent_factory import create_agent
from common.tools import (
    write_contents_to_file,
    RetrieveAdditionalContextTool,
    validate_mermaid_md,
)
from graphs.codegen.agents import (
    create_agent_executor,
    should_invoke_tools,
    invoke_tools,
)
from graphs.codegen.state import AgentState

COLLECTION_NAME = "c4-container-diagram"

retrieve_additional_context_tool = RetrieveAdditionalContextTool(COLLECTION_NAME)

tools = [retrieve_additional_context_tool, write_contents_to_file, validate_mermaid_md]
tool_executor = ToolExecutor(tools)


prompt = ChatPromptTemplate.from_messages(
    [("system", uml_prompt), MessagesPlaceholder(variable_name="messages")]
)

model = ModelFactory.create().bind_tools(tools)
chain = prompt | model

workflow = StateGraph(AgentState)

agent_node = create_agent_executor(chain=chain)

workflow.add_node("agent", agent_node)
workflow.add_node("invoke_tools", partial(invoke_tools, tool_executor=tool_executor))

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    should_invoke_tools,
    {
        "invoke_tools": "invoke_tools",
        "continue": END,
    },
)

# workflow.add_edge("agent", END)
workflow.add_edge("invoke_tools", "agent")

app = workflow.compile()

inputs = {"messages": [HumanMessage(content=user_input)]}

for output in app.stream(inputs):
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")
