import yaml
import json
from typing import Annotated, Type, Any, List, Dict
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


class RetrieveAdditionalContextToolSchema(BaseModel):
    query: str = Field(description="The query to search for.")


class RetrieveAdditionalContextTool(BaseTool):
    """
    This tool queries a vectorstore for additional information.
    """

    name = "retrieve_additional_context"
    description = "Queries a vectorstore for additional information."
    args_schema: Type[BaseModel] = RetrieveAdditionalContextToolSchema
    retriever: Any = None

    def __init__(self, file_info_hash: Dict[str, str], /, **data: Any):
        """
        An agent tool for fetching addition context from a vectorstore.
        """
        super().__init__(**data)
        loader = TextLoader(file_info_hash["file_path"])
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=50
        )
        doc_splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(
            documents=doc_splits,
            collection_name=file_info_hash["collection_name"],
            embedding=AzureOpenAIEmbeddings(),
            persist_directory=".db/chroma_db",
        )
        r = vectorstore.as_retriever()
        self.retriever = r

    def _run(self, query: str) -> str:
        """Use the tool"""
        print(f"[TOOL] retrieving... args: query: {query}")
        return self.retriever.invoke(query)

    async def _arun(self, query: str) -> str:
        """Use the tool"""
        return self._run(query)
