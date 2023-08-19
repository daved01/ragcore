from langchain.schema import Document as LangDocument

from docucite.models.document_model import Document


class DocumentDTO:
    def __init__(self, page_content: str, metadata: dict[str, str]):
        self.page_content = page_content
        self.metadata = metadata

    def to_docucite(self):
        return Document(page_content=self.page_content, metadata=self.metadata)

    def to_langchain(self):
        return LangDocument(page_content=self.page_content, metadata=self.metadata)
