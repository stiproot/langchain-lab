from langchain_openai import AzureChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import PydanticToolsParser
from common.config_loader import load_openai_config

openai_config = load_openai_config()

llm = AzureChatOpenAI(**openai_config)


class add(BaseModel):
    """Add two integers."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


class multiply(BaseModel):
    """Multiply two integers."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


tools = [add, multiply]
llm_with_tools = llm.bind_tools(tools)

# query = "What is 3 * 12?"
query = "What is 3 * 12? Also, what is 11 + 49?"

chain = llm_with_tools | PydanticToolsParser(tools=tools)

resp = chain.invoke(query)

print(resp)
