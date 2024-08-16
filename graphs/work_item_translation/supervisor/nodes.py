from langchain_core.messages import AIMessage, ToolMessage


def agent_node(state, agent, name):
    result = agent.invoke(state)
    if isinstance(result, ToolMessage):
        pass

    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)

    return {"messages": [result], "sender": name}
