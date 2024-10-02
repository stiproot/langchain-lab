from typing import List
import chromadb
import uuid
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from common.model_factory import EmbeddingFactory


class ChromaHttpClientFactory:
    @staticmethod
    def create():
        chroma_client = chromadb.HttpClient(
            settings=Settings(allow_reset=True), host="localhost", port=8000
        )
        return chroma_client


def embed_and_publish(file_paths, collection_name):
    documents = []
    collection = chroma_client.create_collection(collection_name)

    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            embedding = azure_embedding.embed_documents([content])[0]
            documents.append(
                {
                    "id": file_path,
                    "text": content,
                    "embedding": embedding,
                }
            )

    collection.add(documents=documents)


def chunk_embed_and_publish(
    file_paths: List[str],
    collection_name: str,
    embedding_function: AzureOpenAIEmbeddings,
    chroma_client: chromadb.HttpClient,
):
    vector_store = Chroma(
        embedding_function=embedding_function,
        client=chroma_client,
        collection_name=collection_name,
    )

    for file_path in file_paths:
        loader = TextLoader(file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1500, chunk_overlap=50
        )
        doc_splits = text_splitter.split_documents(docs)

        split_texts = [doc.page_content for doc in doc_splits]
        embeddings = embedding_function.embed_documents(split_texts)
        ids = [f"{file_path}_{i}" for i in range(len(split_texts))]

        vector_store.add_documents(documents=doc_splits, embeddings=embeddings, ids=ids)


def create_retriever(
    collection_name, chroma_client, embedding_function: AzureOpenAIEmbeddings
):
    vector_store = Chroma(
        embedding_function=embedding_function,
        collection_name=collection_name,
        client=chroma_client,
    )

    # retriever = vector_store.as_retriever(
    #     search_type="similarity", search_kwargs={"k": 5}
    # )
    retriever = vector_store.as_retriever()

    return retriever
