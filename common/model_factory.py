from langchain_openai import AzureChatOpenAI
from common.config_loader import load_openai_config

openai_config = load_openai_config()


class ModelFactory:
    @staticmethod
    def create():
        llm = AzureChatOpenAI(**openai_config)
        return llm
