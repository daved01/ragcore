import re
from logging import Logger

from ragcore.services.text_splitter_service import TextSplitterService
from ragcore.models.document_model import Document
from ragcore.models.document_loader_model import PDFLoader
from ragcore.shared.errors import UserConfigurationError

PDF_PATTERN = r"\.pdf$"


class DocumentService:
    """
    Document service base class for handling documents.
    Handles uploading, and splitting of documents.

    Pages: pages from the source document
    Documents: split pages from the source document
    """

    def __init__(self, logger: Logger) -> None:
        self.logger: Logger = logger
        self.pages: list[Document] = []
        self.documents: list[Document] = []

    def load_document(self, path: str) -> None:
        """Loads a document into memory.
        Accepts:
        - path: Relative path to document to be uploaded
        """

        filename = path.split("/")[-1]
        title = filename.split(".")[0]

        if not re.search(PDF_PATTERN, filename, re.IGNORECASE):
            raise UserConfigurationError(
                "Prodived document does not have PDF file extension."
            )

        self.logger.info("Loading documents into memory ...")

        loader = PDFLoader(path)
        self.pages = loader.load_and_split(title)

        self.logger.info(
            f"Loaded {len(self.pages)} pages from PDF file with title "
            f"`{title}` from path `{path}`."
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

        splitter = TextSplitterService(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        self.documents = splitter.split_documents(self.pages)
        self.logger.info(
            f"Created {len(self.documents)} documents from {len(self.pages)} pages."
        )
