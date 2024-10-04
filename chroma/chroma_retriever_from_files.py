from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_openai import AzureOpenAIEmbeddings


def get_data():
    with open(".data/wis.md") as f:
        content = f.read()
        return content


file_info_hash = {
    "file_path": ".data/c4.min.md",
    "collection_name": "c4-container-diagram-example",
}

loader = TextLoader(file_info_hash["file_path"])
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000, chunk_overlap=50
)

doc_splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name=file_info_hash["collection_name"],
    embedding=AzureOpenAIEmbeddings(),
    persist_directory=".db/chroma_db",
)

retriever = vectorstore.as_retriever()
