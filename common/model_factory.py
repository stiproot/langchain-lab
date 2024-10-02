from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from common.config_loader import load_openai_config
import os

openai_config = load_openai_config()


class ModelFactory:
    @staticmethod
    def create():
        llm = AzureChatOpenAI(**openai_config)
        return llm


class EmbeddingFactory:
    @staticmethod
    def create():
        azure_embedding = AzureOpenAIEmbeddings(
            deployment="text-embedding-ada-002",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        return azure_embedding
