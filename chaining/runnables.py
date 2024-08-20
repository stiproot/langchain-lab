from typing import List
from typing_extensions import TypedDict
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

class Args(TypedDict):
    a: int
    b: List[int]

def f(x: Args) -> str:
    return str(x["a"] * max(x["b"]))

def p(x: str) -> str:
    return f"Result: {x}"

def s(x: str) -> List[str]:
    return x.split(":")

f_runnable = RunnableLambda(f)
p_runnable = RunnableLambda(p)
s_runnable = RunnableLambda(s)

# as_tool = runnable.as_tool()
# p_as_tool = p_runnable.as_tool()
# output = as_tool.invoke({"a": 3, "b": [1, 2]})

chain = f_runnable | p_runnable | StrOutputParser()

f_chain = f_runnable | p | StrOutputParser()

output = chain.invoke({"a": 3, "b": [1, 2]})
print(output)

output = f_chain.invoke({"a": 3, "b": [1, 2]})
print(output)

