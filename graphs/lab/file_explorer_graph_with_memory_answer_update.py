from typing import Annotated, Literal
from typing_extensions import TypedDict
import json

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import ToolMessage, AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition

from IPython.display import Image, display

from common.config_loader import load_openai_config
from common.tools.walk_folder_tool import walk_folder

openai_config = load_openai_config()

llm = AzureChatOpenAI(**openai_config)

tools = [walk_folder]
llm_with_tools = llm.bind_tools(tools)

memory = SqliteSaver.from_conn_string(":memory:")


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    return {"messages": llm_with_tools.invoke(state["messages"])}


graph_builder = StateGraph(State)

tool_node = ToolNode(tools=tools)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_before=["tools"],
)


# try:
#     display(Image(graph.get_graph().draw_mermaid_png()))
# except Exception:
#     # This requires some extra dependencies and is optional
#     pass

# while True:
#     user_input = input("User: ")
#     if user_input.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")
#         break
#     for event in graph.stream({"messages": ("user", user_input)}):
#         for value in event.values():
#             print("Assistant:", value["messages"])

config = {"configurable": {"thread_id": "1"}}

user_input = "What files are in the following dir? `/Users/simon.stipcich/code/repo/langchain-lab/`. Ignore __pycache__ and .git directories."

events = graph.stream(
    {"messages": [("user", user_input)]}, config, stream_mode="values"
)
for event in events:
    event["messages"][-1].pretty_print()

snapshot = graph.get_state(config)
next = snapshot.next
print("printing next...")
print(next)

existing_message = snapshot.values["messages"][-1]

answer = "Files in the `agents` directory are: `agent.py`, `agent_factory.py`, `agent_manager.py`, `agent_utils.py`."
new_messages = [
    # The LLM API expects some ToolMessage to match its tool call. We'll satisfy that here.
    ToolMessage(content=answer, tool_call_id=existing_message.tool_calls[0]["id"]),
    # And then directly "put words in the LLM's mouth" by populating its response.
    AIMessage(content=answer),
]

new_messages[-1].pretty_print()
graph.update_state(
    # Which state to update
    config,
    # The updated values to provide. The messages in our `State` are "append-only", meaning this will be appended
    # to the existing state. We will review how to update existing messages in the next section!
    {"messages": new_messages},
    as_node="chatbot",
)

print("\n\nLast 2 messages;")
print(graph.get_state(config).values["messages"][-2:])
