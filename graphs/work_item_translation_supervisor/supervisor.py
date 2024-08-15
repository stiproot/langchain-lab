from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from common.model_factory import ModelFactory

members = ["txt_to_yml", "yml_to_json"]


@tool
def who_is_next(params):
    """
    Determine which agent should be called next.
    """

    print(f"Params: {params}")
    next_role = params.get("next")
    print(f"Next role: {next_role}")

    # Validate the 'next' parameter
    if next_role not in members:
        raise ValueError(f"Invalid role. Must be one of {members}. Got: {next_role}")

    return next_role


system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)
# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = ["FINISH"] + members

# Using openai function calling can make output parsing easier for us
# function_def = {
#     "name": "route",
#     "description": "Select the next role.",
#     "parameters": {
#         "title": "routeSchema",
#         "type": "object",
#         "properties": {
#             "next": {
#                 "title": "Next",
#                 "anyOf": [
#                     {"enum": options},
#                 ],
#             }
#         },
#         "required": ["next"],
#     },
# }

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Given the conversation above, who should act next?"
            " Or should we FINISH? Select one of: {options}",
        ),
    ]
).partial(options=str(options), members=", ".join(members))

llm = ModelFactory.create()

supervisor_chain = prompt | llm.bind_tools(tools=[who_is_next])
