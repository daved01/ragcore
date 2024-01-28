from langchain.text_splitter import RecursiveCharacterTextSplitter

from ragcore.models.document_model import Document
from ragcore.dto.document_dto import DocumentDTO


class TextSplitterService:
    """Wrapper for text splitter."""

    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def split_documents(self, documents: list[Document]) -> list[Document]:
        documents_lang = []

        for document in documents:
            document_dto = DocumentDTO(
                page_content=document.page_content, metadata=document.metadata
            )
            documents_lang.append(document_dto.to_langchain())

        splits_lang = self.text_splitter.split_documents(documents=documents_lang)

        splits = []
        for split_lang in splits_lang:
            document_dto = DocumentDTO(
                page_content=split_lang.page_content, metadata=split_lang.metadata
            )
            splits.append(document_dto.to_ragcore())

        return splits
