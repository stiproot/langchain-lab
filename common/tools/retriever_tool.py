import yaml
import json
from typing import Annotated, Type, Any
from pydantic import BaseModel, Field

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.tools.retriever import create_retriever_tool

from langchain_core.tools import BaseTool

def get_data():
    with open(".data/wis.md") as f:
        content = f.read()
        return content

# retriever_tool = create_retriever_tool(
#     retriever,
#     "retrieve_additional_context",
#     "Search and return additional information about the correct structure of work items as YAML.",
# )

class RetrieveAdditionalContextSchema(BaseModel):
    query: str = Field(description="The query to search for.")

class RetrieveAdditionalContext(BaseTool):
    """
    This tool queries a vectorstore for additional information.
    """
    name = "retrieve_additional_context"
    description = "Queries a vectorstore for additional information."
    args_schema: Type[BaseModel] = RetrieveAdditionalContextSchema
    retriever: Any = None

    def __init__(self, /, **data: Any):
        """
        An agent tool for fetching addition context from a vectorstore.
        """
        super().__init__(**data)
        loader = TextLoader(".data/wis.md")
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=50
        )
        doc_splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(
            documents=doc_splits,
            collection_name="work-item-hierarchy-example",
            embedding=AzureOpenAIEmbeddings(),
            persist_directory=".db/chroma_db",
        )
        r = vectorstore.as_retriever()
        self.retriever = r

    def _run(self, query: str) -> str:
        """Use the tool"""
        print("[TOOL] retrieving...")
        return self.retriever.invoke(query)


    async def _arun(self, query: str) -> str:
        """Use the tool"""
        return self._run(query)

