import re
from typing import Any

from ragcore.models.document_model import Document


FILE_EXTENSION_PATTERN = re.compile(r"\.pdf$")


def slice_list(input_list: list[Any], slice_size: int) -> list[list[Any]]:
    """Slices a list into slices of size `slice_size`."""
    num_slices = (len(input_list) // slice_size) + (len(input_list) % slice_size > 0)
    return [
        input_list[i * slice_size : (i + 1) * slice_size] for i in range(num_slices)
    ]


def document_to_str(docs: list[Document]) -> str:
    """Extracts the content from a list of Documents into a line-separated string."""
    docs_text = []
    for _, doc in enumerate(docs):
        docs_text.append(doc.page_content)
    return "\n".join(docs_text)


def remove_file_extension(string: str) -> str:
    """Removes selected file extensions."""
    return FILE_EXTENSION_PATTERN.sub("", string)
