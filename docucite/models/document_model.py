from dataclasses import dataclass


@dataclass
class Document:
    page_content: str
    metadata: dict[str, str]
