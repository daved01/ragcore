from typing import Any, Mapping
from langchain.schema import Document as LangDocument

from ragcore.models.document_model import Document


class DocumentDTO:
    def __init__(self, page_content: str, metadata: Mapping[str, Any]):
        self.page_content = page_content
        self.metadata = metadata

    def to_ragcore(self):
        return Document(page_content=self.page_content, metadata=self.metadata)

    def to_langchain(self):
        return LangDocument(page_content=self.page_content, metadata=self.metadata)

    @staticmethod
    def to_langchain_list(documents: list[LangDocument]) -> list[Document]:
        lang_documents = []
        for document in documents:
            doc_dto = DocumentDTO(
                page_content=document.page_content, metadata=document.metadata
            )
            lang_documents.append(doc_dto.to_ragcore())
        return lang_documents

    @staticmethod
    def to_ragcore_list(lang_documents: list[LangDocument]) -> list[Document]:
        documents = []
        for lang_document in lang_documents:
            doc_dto = DocumentDTO(
                page_content=lang_document.page_content, metadata=lang_document.metadata
            )
            documents.append(doc_dto.to_ragcore())
        return documents
