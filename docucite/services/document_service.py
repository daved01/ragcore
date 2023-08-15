from logging import Logger
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

from docucite.errors import UserConfigurationError


# TODO: Make it ABC
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

    @staticmethod
    def documents_to_texts(documents: list[Document]) -> list[tuple[str, str]]:
        """
        Converts a list of documents to a list of strings and metadata.
        Returns: List of tuples (text, metadata)
        """
        return [(document.page_content, document.metadata) for document in documents]


class DocumentUploadService(DocumentService):
    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)

    # TODO: Add other loaders
    def load_document(self, path: str, document_title: str) -> None:
        """Loads a document into memory.
        Accepts:
        - path: Path to document to be uploaded
        - document_title: Title of document
        Returns:
        - None
        """
        self.logger.info("Uploading documents ...")
        loader = PyPDFLoader(path)
        self.pages = loader.load_and_split()

        # TODO: Must add book page, not pdf page!
        for i, _ in enumerate(self.pages):
            self.pages[i].metadata["title"] = document_title
        self.logger.info(
            f"Loaded pdf file from path `{path}`. Loaded {len(self.pages)} pages."
        )

        self.logger.info(
            f"Added title `{document_title}` to metadata of {len(self.pages)} pages."
        )

    def split_document(self, chunk_size, chunk_overlap) -> None:
        """Splits a document."""
        self.logger.info(
            f"Splitting documents with chunk_size {chunk_size} and chunk_overlap {chunk_overlap} ..."
        )
        # TODO: Add more splitter by type
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        if not self.pages:
            raise UserConfigurationError(
                "No pages to split found. Please upload a document and try again."
            )
        self.documents = splitter.split_documents(self.pages)
        self.logger.info(
            f"Created {len(self.documents)} documents from {len(self.pages)} pages."
        )

    def persist_documents(self):
        pass


class DocumentRetrievalService(DocumentService):
    def __init__(self) -> None:
        super().__init__()

    def retrieve_documents(self):
        pass

    def get_docs_similarity_search(self, question: str, k: int):
        """Returns a set of documents using similarity search."""
        return self.vectordb.similarity_search(query=question, k=k)

    def _document_to_str(self, doc: list[Document]) -> str:
        """Extracts the content from a list of Documents into a line-separated string."""
        docs = []
        for i in range(len(doc)):
            docs.append(doc[i].page_content)
        return "\n".join(docs)
