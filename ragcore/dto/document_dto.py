from typing import Any, Mapping
from langchain.schema import Document as LangDocument

from ragcore.models.document_model import Document


class DocumentDTO:
    """Class for Document Data Transfer Objects to convert to RAG Core documents.

    Example:
        .. code-block:: python

            # Instantiate a DTO
            dto = DocumentDTO(content="This is my text", title="Great text", metadata={"title": "Great text", "page": "1"})

            # Now you can create a ragcore document
            doc = dto.to_ragcore()

    Attributes:
        content: A string for the page content.

        title: The title of the document as a string.

        metadata: A mapping for metadata.

    """

    def __init__(self, content: str, title: str, metadata: Mapping[str, Any]):
        self.content = content
        self.title = title
        self.metadata = metadata

    def to_ragcore(self):
        """Converts to a RAG Core document type."""
        return Document(content=self.content, title=self.title, metadata=self.metadata)

    def to_langchain(self):
        """Converts to a LangChain document type."""
        return LangDocument(page_content=self.content, metadata=self.metadata)

    @staticmethod
    def to_ragcore_list(lang_documents: list[LangDocument]) -> list[Document]:
        """Converts to a list of RAG Core documents.

        Args:
            lang_documents: A list of LangChain documents.

        Returns:
            A list of documents.

        """
        documents = []
        for lang_document in lang_documents:
            doc_dto = DocumentDTO(
                content=lang_document.page_content,
                title=lang_document.metadata.get("title", ""),
                metadata=lang_document.metadata,
            )
            documents.append(doc_dto.to_ragcore())
        return documents
