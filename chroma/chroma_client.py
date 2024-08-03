import chromadb
import uuid
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

loader = TextLoader("../.data/c4.min.md")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

client = chromadb.HttpClient(settings=Settings(allow_reset=True))

collection = client.create_collection("c4-diagrams")

collections_resps = client.list_collections()
print(collections_resps)

collection_resp = client.get_collection("c4-diagrams")
print(collection_resp)


for doc in docs:
    collection.add(
        ids=[str(uuid.uuid1())], metadatas=doc.metadata, documents=doc.page_content
    )
# collection.add(
#     documents=[
#         "Atoms are the building blocks of matter",
#         "Atoms are the Lego blocks of matter",
#     ],
#     metadatas=[{"author": "Simon Stipcich"}, {"source": "Memoirs of a Madman"}],
#     ids=["1", "2"],
# )
query_results = collection.query(query_texts=["Couchbase API"], n_results=1)

embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db4 = Chroma(
    client=client,
    collection_name="c4-diagrams",
    embedding_function=embedding_function,
)
query = "How many components are there in this c4 diagram?"
docs = db4.similarity_search(query)

for d in docs:
    print(d.page_content)
