from langchain_core.tools import tool
import os


@tool
def write_contents_to_file(file_path: str, file_content: str) -> bool:
    """Writes text contents to a specified file path or overwrites existing file contents. Creates the file if it doesn't exist already.

    Args:
      filepath: The file path of the file to write.
      content: The contents to write to file.

    Returns:
      str: A message indicating the file was written to.
    """
    print("Writing to", file_path)

    if os.path.dirname(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)

    return True
