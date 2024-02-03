import re
from logging import Logger

from ragcore.services.text_splitter_service import TextSplitterService
from ragcore.models.document_model import Document
from ragcore.models.document_loader_model import PDFLoader
from ragcore.shared.errors import UserConfigurationError

PDF_PATTERN = r"\.pdf$"


class DocumentService:
    """Handles document interactions.

    The DocumentService class provides methods for creating and processing documents so that
    they can be stored in the database.

    There are two properties related to documents. When a text is first loaded into the system, for
    example from a pdf file, it is parsed into ``pages``, which has one ``Document`` per page. This list
    should then be split into overlapping chunks using the method ``split_pages``. The resulting splits
    are then available in the ``documents`` property.

    Attributes:
        logger: A logger instance.

        pages: A list of ``Document``, representing text which has not been split into chunks.

        documents: A list of ``Document`` of overlapping chunks.

    """

    def __init__(self, logger: Logger) -> None:
        self.logger: Logger = logger
        self.pages: list[Document] = []
        self.documents: list[Document] = []

    def load_texts(self, path: str) -> None:
        """Loads text from a file into memory so it can be processed further.

        Usually, you load text from a file so that it can split into chunks and ingested
        into the database.

        Currently supported file formats are:
            - PDF

        Args:
            path: The string path to a file to be loaded into the service as ``pages``.
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

    def split_pages(self, chunk_size: int, chunk_overlap: int) -> None:
        """Splits pages into overlapping chunks and stores them in documents.

        Must have loaded text with the ``load_texts`` method prior to splitting it.

        Args:
            chunk_size: The size of the chunks.
            chunk_overlap: The overlap of the chunks.

        """
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
