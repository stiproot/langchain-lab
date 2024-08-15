from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI


# def create_agent(
#     llm: AzureChatOpenAI, tools: list, system_prompt: str
# ) -> AgentExecutor:
#     # Each worker node will be given a name and some tools.
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 system_prompt,
#             ),
#             MessagesPlaceholder(variable_name="messages"),
#             MessagesPlaceholder(variable_name="agent_scratchpad"),
#         ]
#     )
#     agent = create_openai_tools_agent(llm, tools, prompt)
#     executor = AgentExecutor(agent=agent, tools=tools)
#     return executor


def create_agent(llm: AzureChatOpenAI, tools: list, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)
