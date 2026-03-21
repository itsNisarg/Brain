"""Tool to create a file with specified content
 and save it to a specific location."""

import os
from typing import Optional


def create_file(filename: str, directory: Optional[str], content: str) -> str:
    """Create a file with the specified content
      and save it to the specified directory.

    Args:
        filename (str): The name of the file to create.
        directory (Optional[str]): The directory to save the file in.
            If None, the file will be created in the current directory.
        content (str): The content to write to the file.

    Returns:
        str: The path of the created file.

    Example:
        create_file("example.txt", "documents", "Hello, world!")
    """
    if directory is not None and not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, filename)\
        if directory is not None else filename

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
    except Exception as e:
        raise RuntimeError(f"Failed to create file '{file_path}': {e}") from e

    return file_path
