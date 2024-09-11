from typing import Tuple
from langchain_core.tools import tool
from .bash import run_bash_cmd
import os


@tool
def validate_mermaid_md(file_path: str) -> Tuple[str, str]:
    """Validates a .md file that contains Mermaid in it.

    Args:
      filepath: The file path of the .md containing Mermaidto validate.

    Returns:
      Tuple[str, str]: A tuple, with the first value being the validation output and the second the error, if there is one.
    """

    command = f"mmdc -i {file_path} -o tmp.md"

    return run_bash_cmd(command)
