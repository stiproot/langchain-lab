from chromadb import EphemeralClient
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from common.config_loader import load_openai_config

openai_config = load_openai_config()


loader = TextLoader(".data/c4.min.md")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = AzureOpenAIEmbeddings()
new_client = EphemeralClient()
openai_lc_client = Chroma.from_documents(
    docs, embeddings, client=new_client, collection_name="c4-diagrams"
)

query = "What components are there in this architecture?"
docs = openai_lc_client.similarity_search(query)
print(docs[0].page_content)
