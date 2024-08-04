from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import PydanticToolsParser
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from common.config_loader import load_openai_config

openai_config = load_openai_config()

llm = AzureChatOpenAI(**openai_config)


@tool
def add(a: int, b: int) -> int:
    """Adds a and b."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiplies a and b."""
    return a * b


tools = {"add": add, "multiply": multiply}

llm_with_tools = llm.bind_tools(tools.values())

query = "What is 3 * 12? Also, what is 11 + 49?"

messages = [HumanMessage(query)]

ai_msg = llm_with_tools.invoke(messages)

messages.append(ai_msg)


for tool_call in ai_msg.tool_calls:
    selected_tool = tools[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)

ai_msg2 = llm_with_tools.invoke(messages)

print(ai_msg2)
