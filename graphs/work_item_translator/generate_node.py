from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from graphs.work_item_translator.model_factory import ModelFactory


def generate(state):
    """
    Generate answer

    Args:
        state (messages): The current state

    Returns:
         dict: The updated state with re-phrased question
    """
    print("---GENERATE---")
    messages = state["messages"]
    question = messages[0].content
    last_message = messages[-1]

    question = messages[0].content
    docs = last_message.content

    prompt = PromptTemplate(
        template="""
        You are work item translator assistant.\n
        You translate raw text into a logical work item tree structure in YAML format.\n
        Use the vector store function to retrieve examples of what the work item tree structure should look like.\n
        Your output should only consist of YAML formatted text.\n
        <context>{context}</context>
        <question>{question}</question>
        """,
        input_variables=["context", "question"],
    )

    # LLM
    llm = ModelFactory.create()

    # Post-processing
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    response = rag_chain.invoke({"context": docs, "question": question})
    return {"messages": [response]}
