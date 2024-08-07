from typing import List, Dict
from langchain_core.tools import tool
from .files import traverse_folder


@tool
def walk_folder(folder_path: str, ignore_folders: List[str]) -> Dict[str, List[str]]:
    """Traverses a folder and returns a dictionary with the folder path as the key and a list of files as the value."""
    return traverse_folder(folder_path=folder_path, ignore_folders=ignore_folders)