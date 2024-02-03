from dataclasses import dataclass
from typing import Any, Mapping


@dataclass
class Document:
    """Model for documents.

    Attributes:
        content: The content of document, as string.

        metadata: A mapping for the metadata.
    """

    content: str
    metadata: Mapping[str, Any]
