from dataclasses import dataclass
from langchain.schema import Document as LDocument


@dataclass
class Document:
    page_content: str
    metadata: dict[str, str]
