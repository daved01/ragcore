from dataclasses import dataclass
from typing import Any, Mapping


@dataclass
class Document:
    """Model for documents.

    Attributes:
        content: The content of document, as string.

        title: The title of the document.

        metadata: A mapping for the metadata.
    """

    content: str
    title: str
    metadata: Mapping[str, Any]
