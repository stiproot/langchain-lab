from common.model_factory import ModelFactory
from graphs.tools import retriever_tool


def agent(state):
    """
    Invokes the agent model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply end.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with the agent response appended to messages
    """
    print("---CALL AGENT---")
    messages = state["messages"]
    model = ModelFactory.create()
    model = model.bind_tools([retriever_tool])
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}
