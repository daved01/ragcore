from dataclasses import dataclass
from typing import Any, Mapping


@dataclass
class Document:
    page_content: str
    metadata: Mapping[str, Any]
