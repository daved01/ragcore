from langchain.text_splitter import RecursiveCharacterTextSplitter

from ragcore.models.document_model import Document
from ragcore.dto.document_dto import DocumentDTO


class TextSplitterService:
    """Handles splitting of text.

    To split the documents, a recursive text splitter is used.

    Attributes:
        chunk_size: The size of the chunks.
        chunk_overlap: The overlap of the chunks.
    """

    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Splits a list of documents into chunks.

        Args:
            documents: A list of ``Document``.

        Returns:
            A list of split documents.

        """
        documents_lang = []

        for document in documents:
            document_dto = DocumentDTO(
                content=document.content, metadata=document.metadata
            )
            documents_lang.append(document_dto.to_langchain())

        splits_lang = self.text_splitter.split_documents(documents=documents_lang)

        splits = []
        for split_lang in splits_lang:
            document_dto = DocumentDTO(
                content=split_lang.page_content, metadata=split_lang.metadata
            )
            splits.append(document_dto.to_ragcore())

        return splits
