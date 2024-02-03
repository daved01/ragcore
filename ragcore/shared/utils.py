import re
from typing import Any

from ragcore.models.document_model import Document


FILE_EXTENSION_PATTERN = re.compile(r"\.pdf$")


def slice_list(input_list: list[Any], slice_size: int) -> list[list[Any]]:
    """Slices a list into slices of size ``slice_size``.

    Args:
        input_list: A list.

        slice_size: The size for a slice.

    Returns:
        A list of sliced elements.
    """
    num_slices = (len(input_list) // slice_size) + (len(input_list) % slice_size > 0)
    return [
        input_list[i * slice_size : (i + 1) * slice_size] for i in range(num_slices)
    ]


def document_to_str(docs: list[Document]) -> str:
    """Extracts the content from a list of Documents into a line-separated string.

    Args:
        docs: A list of documents.

    Returns:
        A string with the document's content.

    """
    docs_text = []
    for _, doc in enumerate(docs):
        docs_text.append(doc.content)
    return "\n".join(docs_text)


def remove_file_extension(string: str) -> str:
    """Removes ``.pdf`` file extensions from a string.

    Args:
        string: A string, possibly with a file extension.

    Returns:
        A string without a file extension.

    """
    return FILE_EXTENSION_PATTERN.sub("", string)
