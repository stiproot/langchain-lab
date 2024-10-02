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

chroma_client = chromadb.HttpClient(
    settings=Settings(allow_reset=True), host="localhost", port=8000
)
azure_embedding = EmbeddingFactory.create()


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


def chunk_embed_and_publish(file_paths, collection_name):
    vector_store = Chroma(
        embedding_function=azure_embedding,
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
        embeddings = azure_embedding.embed_documents(split_texts)
        ids = [f"{file_path}_{i}" for i in range(len(split_texts))]

        vector_store.add_documents(documents=doc_splits, embeddings=embeddings, ids=ids)


def create_retriever(collection_name):
    vector_store = Chroma(
        embedding_function=azure_embedding,
        collection_name=collection_name,
        client=chroma_client,
    )

    # retriever = vector_store.as_retriever(
    #     search_type="similarity", search_kwargs={"k": 5}
    # )
    retriever = vector_store.as_retriever()

    return retriever


# file_paths = ["/Users/simon.stipcich/code/repo/langchain-lab/.data/c4/c4.example.syscontext.md"]
FILE_PATHS = [".data/c4/c4.example.syscontext.md"]
COLLECTION_NAME = "c4-system-context-diagram"

chunk_embed_and_publish(FILE_PATHS, COLLECTION_NAME)

collections = chroma_client.list_collections()
print("COLLECTIONS: ", collections)

collection = chroma_client.get_collection(COLLECTION_NAME)
print("COLLECTION: ", collection)

# query_results = collection.query(
#     query_texts=["What is a C4 System Context diagram?"], n_results=1
# )
# print("COLLECTION QUERY RESULTS: ", query_results)

retriever = create_retriever(COLLECTION_NAME)

QUERY_TEXT = "What is a c4 system context diagram?"
results = retriever.invoke(QUERY_TEXT)

# print(results)

for result in results:
    print(f"Document ID: {result.metadata['source']}")
    print(f"Text: {result.page_content}")
    print("-------")
