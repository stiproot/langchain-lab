import yaml
import json
from typing import Annotated, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from common.utils.logger import log


class MapYmlToJsonSchema(BaseModel):
    yml: str = Field(description="The YAML to map to JSON.")


class MapYmlToJsonTool(BaseTool):
    """
    This tool maps YAML to JSON.
    """

    name: str = "map_yml_to_json"
    description: str = "Converts YAML to JSON."
    args_schema: Type[BaseModel] = MapYmlToJsonSchema

    def _run(self, yml: str) -> str:
        """Use the tool"""
        log(f"{self.name} START.")
        data = yaml.safe_load(yml)
        output = json.dumps(data, indent=2)
        log(f"{self.name} END.")
        return output

    async def _arun(self) -> str:
        """Use the tool"""
        return self._run()
