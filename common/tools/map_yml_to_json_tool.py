import yaml
import json
from typing import Annotated, Type
from pydantic import BaseModel

from langchain_core.tools import BaseTool


class MapYmlToJsonSchema(BaseModel):
    pass

class MapYmlToJsonTool(BaseTool):
    """
    This tool maps YAML to JSON.
    """
    name = "map_yml_to_json"
    description = "Converts YAML to JSON."
    args_schema: Type[BaseModel] = MapYmlToJsonSchema

    def _run(self, yml: str) -> str:
        """Use the tool"""
        data = yaml.safe_load(yml)
        output = json.dump(data, f, indent=1)
        return output


    async def _arun(self) -> str:
        """Use the tool"""
        return self._run()

