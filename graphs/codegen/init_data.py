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
from chroma.chroma_utils import (
    chunk_embed_and_publish,
    create_retriever,
    ChromaHttpClientFactory,
)

FILE_PATHS = [
    ".data/c4/defs/c4.example.def.container.md",
    ".data/c4/c4.example.container.md",
]

COLLECTION_NAME = "c4-container-diagram"


chroma_client = ChromaHttpClientFactory.create()
azure_embedding = EmbeddingFactory.create()


chunk_embed_and_publish(
    file_paths=FILE_PATHS,
    collection_name=COLLECTION_NAME,
    embedding_function=azure_embedding,
    chroma_client=chroma_client,
)

collections = chroma_client.list_collections()
print("COLLECTIONS: ", collections)

collection = chroma_client.get_collection(COLLECTION_NAME)
print("COLLECTION: ", collection)

# query_results = collection.query(
#     query_texts=["What is a C4 System Context diagram?"], n_results=1
# )
# print("COLLECTION QUERY RESULTS: ", query_results)

retriever = create_retriever(
    collection_name=COLLECTION_NAME,
    chroma_client=chroma_client,
    embedding_function=azure_embedding,
)

QUERY_TEXT = "What is a c4 container diagram?"
results = retriever.invoke(QUERY_TEXT)

# print(results)

for result in results:
    print(f"Document ID: {result.metadata['source']}")
    print(f"Text: {result.page_content}")
    print("-------")
