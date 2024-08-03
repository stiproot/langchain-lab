from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

loader = TextLoader("../.data/c4.min.md")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db2 = Chroma.from_documents(
    docs, embedding_function, persist_directory="../.db/chroma_db"
)

query = "How many components are there in this c4 diagram?"
# docs = db2.similarity_search(query)

db3 = Chroma(persist_directory="../.db/chroma_db", embedding_function=embedding_function)
docs = db3.similarity_search(query)

for d in docs:
    print(d.page_content)
