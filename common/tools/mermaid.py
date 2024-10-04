from typing import Tuple, Optional
from langchain_core.tools import tool
from .bash import run_bash_cmd
import os


@tool
def validate_mermaid_md(
    file_path: str, output_img_path: Optional[str] = None
) -> Tuple[str, str]:
    """Validates a .md file that contains Mermaid in it, by converting it to an image using Mermaid CLI.

    Args:
      filepath: The file path of the .md containing Mermaidto validate.
      output_img_path: The output image path to save the image to. Defaults to None.

    Returns:
      Tuple[str, str]: A tuple, with the first value being the validation output and the second the error, if there is one.
    """

    output_file_path = output_file_path or "tmp.md"

    command = f"mmdc -i {file_path} -o {output_file_path}"

    return run_bash_cmd(command)
