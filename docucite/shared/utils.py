from typing import Any

from docucite.models.document_model import Document


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
