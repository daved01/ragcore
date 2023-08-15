from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema.document import Document
from logging import Logger
import os

from docucite.constants import AppConstants
from docucite.errors import DatabaseError
from docucite.model import VectorDatabase
from docucite.services.document_service import DocumentService


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

    def create_database(self) -> None:
        """
        Creates a new database if it does not already exist and saves it on disk
        in the path `AppConstants.DATABASE_BASE_DIR`.
        """
        if self._dir_exists(self.database_path):
            raise DatabaseError(
                f"Cannot create database `{self.database_path}` because it already exists."
            )

        if not self._dir_exists(AppConstants.DATABASE_BASE_DIR):
            self._create_base_dir()

        self.vectordb = Chroma(
            persist_directory=self.database_path, embedding_function=self.embedding
        )

        self.logger.info(f"Created database in path `{self.database_path}`.")

    def load_database(self) -> None:
        """Loads an existing vector database into memory."""
        if not self._dir_exists(self.database_path):
            raise DatabaseError(
                f"Tried to load database `{self.database_path}`, but it does not exist."
            )
        self.logger.info(f"Loading from database in path {self.database_path} ...")

        self.vectordb = Chroma(
            persist_directory=self.database_path, embedding_function=self.embedding
        )
        self.logger.info(
            f"Successfully loaded database `{self.database_path}` with {len(self.vectordb.get().get('ids', -1))} indexed documents."
        )

    def add_documents(self, documents: list[Document]) -> None:
        """Adds documents to existing database."""
        # Check if database exists on disk. If not exit.
        if not self.vectordb:
            raise DatabaseError(
                f"Tried to add documents to database `{self.database_path}`, "
                "but this database does not exist."
            )

        # Update database
        self.logger.info(
            f"Adding {len(documents)} documents to database at `{self.database_path}`."
        )
        new_data = DocumentService.documents_to_texts(documents)
        new_texts, new_metadatas = map(list, zip(*new_data))

        self.vectordb.add_texts(texts=new_texts, metadatas=new_metadatas)

        self.logger.info(
            f"Successfully added {len(documents)} documents to database. "
            f"Number of indexed documents is now: {len(self.vectordb.get().get('ids', -1))}",
        )

    def _create_base_dir(self) -> None:
        """Helper to make sure database base dir exists."""
        self.logger.info(
            f"Creating base dir for database `{AppConstants.DATABASE_BASE_DIR}` ..."
        )
        if not os.path.exists(AppConstants.DATABASE_BASE_DIR):
            os.makedirs(AppConstants.DATABASE_BASE_DIR)

    @staticmethod
    def _dir_exists(dir) -> bool:
        return os.path.exists(dir) and os.path.isdir(dir) if dir else False
