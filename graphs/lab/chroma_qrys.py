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
from agnt_smth.core.utls import (
    EmbeddingFactory,
    chunk_embed_and_publish,
    create_retriever,
    ChromaHttpClientFactory,
)

azure_embedding = EmbeddingFactory.create()

chroma_client = ChromaHttpClientFactory.create_with_auth()
# chroma_client = chromadb.HttpClient(host="chromadb-lexi", port=8000)
# chroma_client = chromadb.HttpClient(settings=Settings(allow_reset=True, chroma_client_auth_provider="chromadb.auth.basic_authn.BasicAuthClientProvider", chroma_client_auth_credentials="admin:admin"), host="localhost", port=8000)
print(chroma_client.heartbeat())  # this should work with or without authentication - it is a public endpoint


# collections = chroma_client.list_collections()
# print("COLLECTIONS: ", collections)

# collection = chroma_client.get_collection("Internal-Lexi")
# print("COLLECTION: ", collection)

# retriever = create_retriever(
#     collection_name="Internal-Lexi",
#     chroma_client=chroma_client,
#     embedding_function=azure_embedding,
# )

# QUERY_TEXT = "What is Lexi?"
# results = retriever.invoke(QUERY_TEXT)

# for result in results:
#     print(f"Document ID: {result.metadata['source']}")
#     print(f"Text: {result.page_content}")
#     print("-------")
