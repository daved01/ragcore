from logging import Logger
import os
from typing import Optional

from docucite.errors import DatabaseError, MissingMetadataError, InvalidMetadataError
from docucite.models.document_model import Document
from docucite.models.embedding_model import Embedding
from docucite.models.database_model import VectorDataBaseModel
from docucite.services.document_service import DocumentService


Metadata = dict[str, str]


class DatabaseService:
    """
    Creates a DatabaseService.
    To initialize a service with a database in memory only, pass database_name=None to the
    initializer.
    """

    def __init__(
        self,
        logger: Logger,
        database_base_path: str,
        database_name: str,
        embedding_model: str,
        num_search_results: int,
    ) -> None:
        self.logger: Logger = logger
        self.base_path: str = database_base_path
        self.database_name: Optional[str] = database_name if database_name else None
        self.full_path: str = (
            self.base_path + "/" + database_name if database_name else self.base_path
        )
        self.number_search_results: int = num_search_results
        self.vectordb: Optional[VectorDataBaseModel] = None
        self.embedding: Embedding = Embedding(model=embedding_model)

    def create_database(self) -> None:
        """
        Creates a new database if it does not already exist and saves it on disk
        in the path `database_path`.
        """

        if (
            self.full_path
            and os.path.exists(self.full_path)
            and os.path.isdir(self.full_path)
        ):
            raise DatabaseError(
                f"Cannot create database `{self.full_path}` because it already exists."
            )

        if not (
            self.base_path
            and os.path.exists(self.base_path)
            and os.path.isdir(self.base_path)
        ):
            self._create_base_dir()

        self.vectordb = VectorDataBaseModel(
            persist_directory=self.full_path, embedding_function=self.embedding
        )

        self.logger.info(f"Created database in path `{self.full_path}`.")

    def load_database(self) -> None:
        """Loads an existing vector database into memory."""
        if not (
            self.full_path
            and os.path.exists(self.full_path)
            and os.path.isdir(self.full_path)
        ):
            raise DatabaseError(
                f"Tried to load database `{self.full_path}`, but it does not exist."
            )
        self.logger.info(f"Loading from database in path {self.full_path} ...")

        self.vectordb = VectorDataBaseModel(
            persist_directory=self.full_path, embedding_function=self.embedding
        )
        self.logger.info(
            f"Successfully loaded database `{self.full_path}` with "
            f"{len(self.vectordb.get().get('ids', -1))} indexed documents."
        )

    def add_documents(self, documents: list[Document]) -> None:
        """
        Adds documents to an existing database.
        Documents must have metadata, and the metadata must have a `title` specified.
        Adding documents with the same title multiple times is not possible.
        """
        # Check if database exists on disk. If not exit.
        if not self.vectordb:
            raise DatabaseError(
                f"Tried to add documents to database `{self.full_path}`, "
                "but this database does not exist."
            )

        new_datas: list[tuple[str, Metadata]] = DocumentService.documents_to_texts(
            documents
        )

        new_texts, new_metadatas = self._extract_data(new_datas)

        # Check if we can add the new documents
        self._validate_documents_metadata(texts=new_texts, metadatas=new_metadatas)
        self._validate_documents_not_in_database(metadatas=new_metadatas)

        # Update database
        self.logger.info(
            f"Adding {len(documents)} documents to database at `{self.full_path}`."
        )

        self.vectordb.add_texts(texts=new_texts, metadatas=new_metadatas)

        self.logger.info(
            f"Successfully added {len(documents)} documents to database. "
            f"Number of indexed documents is now: {len(self.vectordb.get().get('ids', -1))}",
        )

    def search(self, query: str) -> list[Document]:
        """Returns a list of documents for a query."""
        if not self.vectordb:
            raise DatabaseError(
                "Database does not exist. Please create it before running a search."
            )

        return self.vectordb.similarity_search(query, k=self.number_search_results)

    def _validate_documents_metadata(
        self, texts: list[str], metadatas: list[Metadata]
    ) -> None:
        if not metadatas or not len(texts) == len(metadatas):
            raise MissingMetadataError(
                "At least one document you are trying to add has missing metadata."
            )

        for metadata in metadatas:
            if not metadata.get("title"):
                raise InvalidMetadataError("Metadata does not have a title.")

    # We want the documents in the database to be unique, which we enforce through the metadata
    # field `title`. We assume that the metadata with which this method is called is valid.
    def _validate_documents_not_in_database(
        self, metadatas: list[dict[str, str]]
    ) -> None:
        if not self.vectordb:
            raise DatabaseError(
                "Tried to validate documents in database, "
                "but the database has not been initialized."
            )

        vectordb_titles = self.vectordb.get().get("metadatas")

        existing_titles = (
            set(title.get("title").lower() for title in vectordb_titles)
            if vectordb_titles
            else set()
        )
        new_titles = set(title.get("title", "").lower() for title in metadatas)

        union = new_titles & existing_titles
        if union:
            raise DatabaseError(
                f"Tried to add documents {union} to database, but they already exist."
            )

    def _create_base_dir(self) -> None:
        """Helper to make sure database base dir exists."""
        self.logger.info(f"Creating base dir for database `{self.base_path}` ...")
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    @staticmethod
    def _extract_data(
        datas: list[tuple[str, Metadata]]
    ) -> tuple[list[str], list[Metadata]]:
        new_texts = []
        new_metadatas = []
        for data in datas:
            new_texts.append(data[0])
            new_metadatas.append(data[1])

        return new_texts, new_metadatas
