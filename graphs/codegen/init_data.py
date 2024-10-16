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
from graphs.codegen.data_types import COLLECTION_NAMES, C4_DIAGRAM_TYPES

FILE_INFO = {
    COLLECTION_NAMES.C4_SYSCONTEXT_DIAG.value: {
        ".data/c4/defs/c4.example.def.syscontext.md",
    },
    COLLECTION_NAMES.C4_CONTAINER_DIAG.value: {
        ".data/c4/defs/c4.example.def.container.md",
        ".data/c4/c4.example.container.md",
    },
    COLLECTION_NAMES.C4_COMPONENT_DIAG.value: {
        ".data/c4/defs/c4.example.def.component.md",
    },
    COLLECTION_NAMES.F4_LANG_LIB.value: {
        ".data/f4-lang/f4-lang.examples.md",
        ".data/f4-lang/f4-lang.detail.md",
        ".data/f4-lang/f4-lang.ifthen.md",
    },
}

chroma_client = ChromaHttpClientFactory.create()
azure_embedding = EmbeddingFactory.create()

for collection_name, file_paths in FILE_INFO.items():

    chunk_embed_and_publish(
        file_paths=file_paths,
        collection_name=collection_name,
        embedding_function=azure_embedding,
        chroma_client=chroma_client,
    )

    # collections = chroma_client.list_collections()
    # print("COLLECTIONS: ", collections)

    # collection = chroma_client.get_collection(COLLECTION_NAMES.C4_CONTAINER_DIAG.value)
    # print("COLLECTION: ", collection)

    # query_results = collection.query(
    #     query_texts=["What is a C4 System Context diagram?"], n_results=1
    # )
    # print("COLLECTION QUERY RESULTS: ", query_results)

    # retriever = create_retriever(
    #     collection_name=COLLECTION_NAMES.C4_CONTAINER_DIAG.value,
    #     chroma_client=chroma_client,
    #     embedding_function=azure_embedding,
    # )

    # QUERY_TEXT = "What is a c4 container diagram?"
    # results = retriever.invoke(QUERY_TEXT)

    # for result in results:
    #     print(f"Document ID: {result.metadata['source']}")
    #     print(f"Text: {result.page_content}")
    #     print("-------")
