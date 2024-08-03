import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host="localhost", port=8000, settings=Settings(allow_reset=True)
)

client.reset()
