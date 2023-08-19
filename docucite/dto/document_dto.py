from langchain.schema import Document as LangDocument

from docucite.models.document_model import Document


# TODO: Tests
class DocumentDTO:
    def __init__(self, page_content: str, metadata: dict[str, str]):
        self.page_content = page_content
        self.metadata = metadata

    @classmethod
    def from_docucite(cls, document: Document):
        return cls(page_content=document.page_content, metadata=document.metadata)

    @classmethod
    def from_langchain(cls, lang_document: LangDocument):
        return cls(
            page_content=lang_document.page_content, metadata=lang_document.metadata
        )

    def to_docucite(self):
        return Document(page_content=self.page_content, metadata=self.metadata)

    def to_langchain(self):
        return LangDocument(page_content=self.page_content, metadata=self.metadata)
