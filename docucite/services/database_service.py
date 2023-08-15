from logging import Logger
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema.document import Document
import os

from docucite.errors import DatabaseError
from docucite.constants import AppConstants
from docucite.model import VectorDatabase
from docucite.services.document_service import DocumentService


# TODO: Make singleton?
class DatabaseService:
    """
    Creates a DatabaseService.
    To initialize a service with a database in memory only, pass database_name=None to the
    initializer.
    """

    def __init__(
        self,
        logger: Logger,
        database_name: str,
    ) -> None:
        self.logger: Logger = logger
        self.database_path: str = (
            AppConstants.DATABASE_BASE_DIR + "/" + database_name
            if database_name
            else None
        )
        self.vectordb: VectorDatabase = None
        self.embedding: OpenAIEmbeddings = OpenAIEmbeddings()

    # TODO: Does 2 things. Creates database, and adds documents.
    def create_database(self, documents: list[Document]) -> None:
        # Check if database dir exists. If so, exit.
        if self._dir_exists(self.database_path):
            raise DatabaseError("Database already exists.")

        # Create base folder data if not exist
        if not self._dir_exists(AppConstants.DATABASE_BASE_DIR):
            self._create_base_dir()

        # Create database
        self.vectordb = Chroma.from_documents(
            documents, self.embedding, persist_directory=self.database_path
        )
        self.logger.info(f"Loaded {len(documents)} documents into DatabaseService.")

    # TODO: Test? What id path does not exist? -> Creates a new database in the path
    def load_database(self) -> None:
        """Loads an existing vector database into memory."""
        self.logger.info(f"Loading from database in path {self.database_path} ...")
        self.vectordb = Chroma(
            persist_directory=self.database_path, embedding_function=self.embedding
        )
        self.logger.info(f"Successfully loaded database!")

    def update_database(self, documents: list[Document]) -> None:
        """
        Adds documents to existing database.
        The database must exist on disk or in memory.
        """
        # Check if database exists on disk. If not exit.
        if not self.vectordb:
            raise DatabaseError(
                f"Tried to load database `{self.database_path}`, "
                "but it neither exists on disk, nor in memory."
            )

        # Update database
        self.logger.info(
            f"Adding {len(documents)} documents to database at {self.database_path}."
        )
        num_docs_before = len(self.vectordb.get().get("ids", -1))
        new_data = DocumentService.documents_to_texts(documents)
        new_texts, new_metadatas = map(list, zip(*new_data))

        self.vectordb.add_texts(texts=new_texts, metadatas=new_metadatas)

        self.logger.info(
            f"Number of indexed documents before, after: {num_docs_before} | {self.vectordb.get().get('ids', -1)}"
        )

    def _create_base_dir(self) -> None:
        """Helper to make sure base dir exists."""
        self.logger.info(
            f"Creating base dir for database `{AppConstants.DATABASE_BASE_DIR}` ..."
        )
        if not os.path.exists(AppConstants.DATABASE_BASE_DIR):
            os.makedirs(AppConstants.DATABASE_BASE_DIR)

    @staticmethod
    def _dir_exists(dir) -> bool:
        return os.path.exists(dir) and os.path.isdir(dir) if dir else False
