import os
from typing import List, Dict
from langchain_core.tools import tool
from common.utils.logger import log


@tool
def write_contents_to_file(file_path: str, file_content: str) -> bool:
    """Writes text contents to a specified file path or overwrites existing file contents. Creates the file if it doesn't exist already.

    Args:
      filepath: The file path of the file to write.
      content: The contents to write to file.

    Returns:
      str: A message indicating the file was written to.
    """

    log(f"write_contents_to_file START. file_path: {file_path}")

    if os.path.dirname(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)

    log(f"write_contents_to_file END. file_path: {file_path}")

    return True


@tool
def read_file_contents(file_path: str) -> str:
    """Reads the contents of a file.

    Args:
      file_path: The path to the file to read.

    Returns:
      str: The contents of the file.
    """

    log(f"read_file_contents START. file_path: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def traverse_folder(folder_path, ignore_folders):

    log(f"traverse_folder START. folder_path: {folder_path}")

    file_dict = {}

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in ignore_folders]

        file_dict[root] = files

    log(f"traverse_folder END.")

    return file_dict


@tool
def walk_folder(folder_path: str, ignore_folders: List[str]) -> Dict[str, List[str]]:
    """Traverses a folder and returns a dictionary with the folder path as the key and a list of files as the value."""
    return traverse_folder(folder_path=folder_path, ignore_folders=ignore_folders)
