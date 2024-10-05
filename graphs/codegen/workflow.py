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


user_input = """
    Use case:
    As as user, I would like to translate a meeting transcript into Azure DevOps Work Items.
    I would like to upload the transcript to a web application, and have it build a work item hierarchy.
    If I approve the hierarchy, I would like the web application to create the work items in Azure DevOps.

    Technical requirements:
    - The system should be able to handle 1000 requests per second.
    - The system should be able to store 1TB of data.
    - The system should use a NoSQL database.
    - The system should be able to scale horizontally.
    - The system should use Dapr for microservices.
    - Vue.js should be used for the frontend.
    - Python should be used for the backend.
 
    Write the output to `/Users/simon.stipcich/code/repo/langchain-lab/graphs/codegen/.output/c4-container-diag.md`.
    """

uml_prompt = f"""
    You are a UML design agent with expertise in creating C4 component diagrams using Mermaid syntax. 
    
    Your primary task is to assist in designing software architectures in generating C4 component diagrams. You should follow these guidelines:

    Understand the Requirements: use the context retriever tool to look up examples of a C4 component diagram and understand the requirements for the diagram. 

    Use Mermaid Syntax: Generate the diagrams using Mermaid syntax, ensuring that the structure follows C4 model principles (Context, Container, Component, and Code diagrams).

    Focus on Clarity and Accuracy: Ensure that the diagrams are clear, concise, and easy to understand, accurately representing the architectural components and their relationships.

    Provide Explanations: Along with the diagram, provide a brief explanation of the components, their purpose, and their interactions.

    Validate: Use the Mermaid validation tool to ensure that the Mermaid syntax is correct. If there are any errors, fix them. Output any test artifacts that are generated during validation to the location specified by the user.

    Iterate Based on Feedback: If revisions are needed, ask for specific feedback and modify the diagrams accordingly.
    """

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
