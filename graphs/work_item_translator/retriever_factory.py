from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.tools.retriever import create_retriever_tool


def get_data():
    with open(".data/wis.md") as f:
        content = f.read()
        return content


loader = TextLoader(".data/wis.md")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, chunk_overlap=50
)
doc_splits = text_splitter.split_documents(docs)

vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="work-item-hierarchy-example",
    embedding=AzureOpenAIEmbeddings(),
    persist_directory=".db/chroma_db",
)
retriever = vectorstore.as_retriever()


retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_blog_posts",
    "Search and return information about Lilian Weng blog posts on LLM agents, prompt engineering, and adversarial attacks on LLMs.",
)

tools = [retriever_tool]
