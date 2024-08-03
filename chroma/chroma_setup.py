from chromadb import Client
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever


def get_data():
    with open("../.data/c4.min.md") as f:
        content = f.read()
        print(content)
        return content


chroma_client = Client(chroma_url="http://localhost:8000")
chroma_vector_store = Chroma()
embedding_model = AzureOpenAIEmbeddings()


documents = [get_data()]
embeddings = [embedding_model.embed(doc) for doc in documents]
doc_ids = ["c4"]

for doc_id, doc, embedding in zip(doc_ids, documents, embeddings):
    chroma_vector_store.add(doc_id=doc_id, embedding=embedding, document=doc)


retriever = VectorStoreRetriever(vector_store=chroma_vector_store)

query = "What database technology is being used"

retrieved_docs = retriever.retrieve(query)
for doc in retrieved_docs:
    print(f"Document ID: {doc.doc_id}, Content: {doc.document}")
