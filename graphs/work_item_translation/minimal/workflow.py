from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph.message import MessageGraph

builder = MessageGraph()
builder.add_node(
    "chatbot",
    lambda state: [
    AIMessage(
        content="Hello!",
        tool_calls=[{"name": "search", "id": "123", "args": {"query": "X"}}],
        )
    ],
)
builder.add_node(
    "search", lambda state: [ToolMessage(content="Searching...", tool_call_id="123")]
)
builder.set_entry_point("chatbot")
builder.add_edge("chatbot", "search")
builder.set_finish_point("search")
builder.compile().invoke([HumanMessage(content="Hi there. Can you search for X?")])
