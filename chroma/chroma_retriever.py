from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

loader = TextLoader(".data/c4.min.md")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db = Chroma.from_documents(docs, embedding_function)
retriever = db.as_retriever(search_type="mmr")

query = "What did the president say about Ketanji Brown Jackson"
docs = retriever.invoke(query)

for d in docs:
  print(d.page_content)