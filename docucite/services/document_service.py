from logging import Logger
from typing import Any
from langchain.text_splitter import RecursiveCharacterTextSplitter

from docucite.models.document_model import Document
from docucite.models.document_loader_model import PDFLoader
from docucite.errors import UserConfigurationError


class DocumentService:
    """
    Document service base class for handling documents.
    Handles uploading, splitting of documents.

    Pages: pages from the source document
    Documents: split pages from the source document
    """

    def __init__(self, logger: Logger) -> None:
        self.logger: Logger = logger
        self.pages: list[Document] = []
        self.documents: list[Document] = []

    def load_document(self, path: str, document_title: str) -> None:
        """Loads a document into memory.
        Accepts:
        - path: Path to document to be uploaded
        - document_title: Title of document
        """
        self.logger.info("Loading documents into memory ...")

        loader = PDFLoader(path)
        self.pages = loader.load_and_split()

        # TODO: Must add book page, not pdf page! # pylint: disable=fixme
        for i, _ in enumerate(self.pages):
            self.pages[i].metadata["title"] = document_title

        self.logger.info(
            f"Loaded {len(self.pages)} pages from PDF file with title "
            f"`{document_title}` from path `{path}`."
        )

    def split_document(self, chunk_size: int, chunk_overlap: int) -> None:
        """Splits a document."""
        if not self.pages:
            raise UserConfigurationError(
                "No pages to split found. Please upload a document and try again."
            )

        self.logger.info(
            f"Splitting {len(self.pages)} pages with chunk_size {chunk_size} "
            f"and chunk_overlap {chunk_overlap} ..."
        )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        self.documents = splitter.split_documents(self.pages)
        self.logger.info(
            f"Created {len(self.documents)} documents from {len(self.pages)} pages."
        )

    @staticmethod
    def documents_to_texts(
        documents: list[Document],
    ) -> list[tuple[str, dict[str, str]]]:
        """
        Converts a list of documents to a list of strings and metadata.
        Returns: List of tuples (text, metadata)
        """
        return [(document.page_content, document.metadata) for document in documents]
