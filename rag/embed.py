from typing import List, Optional, Any, Dict
import uuid
import base64

import chromadb
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000
DEFAULT_USR = "admin"
DEFAULT_PWD = "admin"
DEFAULT_CHUNK_SIZE = 1500
DEFAULT_CHUNK_OVERLAP = 50


def chunk_files(
    file_paths: List[str],
    chunk_size: int,
    chunk_overlap: int
) -> Dict[str, Dict[str, Any]]:

    chunk_hash = {}

    for file_path in file_paths:
        loader = TextLoader(file_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        split_docs = text_splitter.split_documents(docs)
        split_texts = [doc.page_content for doc in split_docs]

        if not len(split_texts):
            continue

        chunk_hash[file_path] = {"split_docs": split_docs, "split_texts": split_texts}

    return chunk_hash


def create_chroma_client():
    auth_str = f"{DEFAULT_USR}:{DEFAULT_PWD}"
    chroma_client = chromadb.HttpClient(
        settings=Settings(allow_reset=True, chroma_client_auth_provider="chromadb.auth.basic_authn.BasicAuthClientProvider", chroma_client_auth_credentials=auth_str), 
        host=DEFAULT_HOST,
        port=DEFAULT_PORT
    )
    return chroma_client


def chunk_embed_and_publish(
    file_paths: List[str],
    collection_name: str,
    embedding_function: Any,
    chroma_client: chromadb.HttpClient,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,

):
    vector_store = Chroma(
        embedding_function=embedding_function,
        client=chroma_client,
        collection_name=collection_name,
    )

    chunked_file_hash = chunk_files(file_paths, chunk_size, chunk_overlap)

    for file_path in chunked_file_hash:

        split_docs = chunked_file_hash[file_path]["split_docs"]
        split_texts = chunked_file_hash[file_path]["split_texts"]

        embeddings = embedding_function.embed_documents(split_texts)
        ids = [f"{file_path}_{i}" for i in range(len(embeddings))]

        if not len(ids):
            continue

        vector_store.add_documents(documents=split_docs, embeddings=embeddings, ids=ids)


def create_retriever(
    collection_name: str, chroma_client: chromadb.HttpClient, embedding_function: Any
):
    vector_store = Chroma(
        embedding_function=embedding_function,
        collection_name=collection_name,
        client=chroma_client,
    )
    retriever = vector_store.as_retriever()
    return retriever


if __name__ == "__main__":
    file_paths = [".data/c4/defs/c4.example.def.syscontext.md"]
    collection_name = "tmp-chroma"
    chroma_client = create_chroma_client()
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # chunk_embed_and_publish(
    #     file_paths=file_paths,
    #     collection_name=collection_name,
    #     embedding_function=embedding_function,
    #     chroma_client=chroma_client,
    # )

    retriever = create_retriever(
        collection_name=collection_name,
        chroma_client=chroma_client,
        embedding_function=embedding_function,
    )
    query = "what is a c4 system context diagram?"
    results = retriever.invoke(query, k=5)

    for result in results:
        print(result)

