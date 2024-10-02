from json import load as json_load
import os


def load_openai_config(config_file_path: str = ".config/openai_config.json"):
    with open(config_file_path) as f:
        openai_config = json_load(f)
        os.environ["AZURE_OPENAI_API_KEY"] = openai_config["openai_api_key"]
        os.environ["AZURE_OPENAI_ENDPOINT"] = openai_config["azure_endpoint"]
        os.environ["AZURE_OPENAI_API_VERSION"] = openai_config["openai_api_version"]
        return openai_config
