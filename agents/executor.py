import os

from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent

from common.model_factory import ModelFactory

llm = ModelFactory.create()

@tool
def write_contents_to_file(filepath: str, content: str) -> str:
  """Writes text contents to a specified file path or overwrites existing file contents. Creates the file if it doesn't exist already.

  Args:
    filepath: The file path of the file to write.
    content: The contents to write to file.

  Returns:
    str: A message indicating the file was written to.
  """
  print("Writing to", filepath)

  if os.path.dirname(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

  with open(filepath, "w", encoding="utf-8") as f:
      f.write(content)

  return f"Content was written to {filepath}."


def run_agent(input_text):
  
  # Define tools
  tools = [write_contents_to_file]

  # Build initial prompt
  prompt = ChatPromptTemplate.from_messages([
      ("system", "You are a helpful assistant that is an expert in Python."),
      ("human", "{input_text}"),
      MessagesPlaceholder(variable_name='agent_scratchpad')
  ])

  # Initialize the agent with the tools
  agent = create_openai_tools_agent(llm, tools, prompt)

  # Initialize the agent executor (adds a memory component to the agent)
  agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)

  response = agent_executor.invoke({"input_text": input_text})

  return response

# Use the agent executor
input_text = """"Write me a Flask application that returns the response 'Hello World!' as an alert when a user clicks a button on a front end at localhost:5000/.

Write all necessary files to disk at the following location: /Users/simon.stipcich/code/repo/langchain-lab/agents/.executor_output/"""

# Run the agent to generate the code. Then run `python app.py` and navigate to http://localhost:5000/ to view the app.
result = run_agent(input_text)

print(result)
