from logging import Logger
import os
from typing import Optional, Mapping

from ragcore.shared.constants import (
    ConfigurationConstants,
    DatabaseConstants,
    DataConstants,
    EmbeddingConstants,
)
from ragcore.shared.errors import DatabaseError, MetadataError, EmbeddingError
from ragcore.models.document_model import Document
from ragcore.models.embedding_model import (
    BaseEmbedding,
    OpenAIEmbedding,
    AzureOpenAIEmbedding,
)
from ragcore.models.database_model import BaseVectorDatabaseModel, ChromaDatabase
from ragcore.shared import utils

Metadata = dict[str, str]


class DatabaseService:
    """Handles database interactions.

    The DatabaseService class provides methods for interacting with the database, allowing you to perform operations
    such as adding documents, querying information, and managing the knowledge store. Based on the configuration, either
    a local or a remote database is managed by the service. The interactions with the database are implemented in the model layer.

    Attributes:
        logger: A logger instance

        base_path: The path to the local database as a string.

        name: The name of the database

        num_search_results: The number of results which are returned for a query.

        embedding_config: A configuration for the embedding, usually the embedding part of the config file.

    """

    def __init__(
        self,
        logger: Logger,
        base_path: Optional[str],
        name: Optional[str],
        num_search_results: int,
        embedding_config: Mapping[str, str],
    ) -> None:
        self.logger: Logger = logger
        self.base_path: Optional[str] = base_path
        self.name: Optional[str] = name if name else None
        self.number_search_results: int = num_search_results
        self.embedding: BaseEmbedding = self._init_embedding(config=embedding_config)
        self.database: Optional[BaseVectorDatabaseModel] = None

    def _init_embedding(self, config: Mapping[str, str]) -> BaseEmbedding:
        """Initializes an embedding model."""
        provider = config.get(ConfigurationConstants.KEY_EMBEDDING_PROVIDER)
        model = config.get(ConfigurationConstants.KEY_EMBEDDING_MODEL)
        api_version = config.get(
            ConfigurationConstants.KEY_EMBEDDING_AZURE_OPENAI_API_VERSION, ""
        )
        endpoint = config.get(
            ConfigurationConstants.KEY_EMBEDDING_AZURE_OPENAI_AZURE_ENDPOINT, ""
        )
        if not provider or not model:
            raise EmbeddingError("Provider or model missing in the configuration.")

        if provider == EmbeddingConstants.PROVIDER_OPENAI:
            self.logger.info(
                f"Using embedding model {model}, provider `{EmbeddingConstants.PROVIDER_OPENAI}`."
            )
            return OpenAIEmbedding(model=model)
        if provider == EmbeddingConstants.PROVIDER_AZURE_OPENAI:
            self.logger.info(
                f"Using embedding model {model}, provider `{EmbeddingConstants.PROVIDER_AZURE_OPENAI}`."
            )
            return AzureOpenAIEmbedding(
                model=model, api_version=api_version, endpoint=endpoint
            )
        raise EmbeddingError(f"Selected embedding provider {provider} not supported.")

    def initialize_local_database(self) -> None:
        """Initializes a local database.

        To initialize a local database, the DatabaseService must have the attributes ``base_path`` and ``name`` set.
        If the base path does not exist it is created.

        """
        if not self.name or not self.base_path:
            raise DatabaseError(
                "Tried to initialize a local database, but no name and/or path for it is given."
            )

        # Create base path if it does not exist
        if not (os.path.exists(self.base_path) and os.path.isdir(self.base_path)):
            self._create_base_dir()

        if self.name and DatabaseConstants.PROVIDER_CHROMA in self.name:
            self.database = ChromaDatabase(
                persist_directory=self.base_path + "/" + self.name,
                num_search_results=self.number_search_results,
                embedding_function=self.embedding,
            )
        else:
            raise DatabaseError(
                f"Specified database {self.name.split('_')[0] if self.name else '<no-name>'} is not supported."
            )

        self.logger.info(
            f"Initialized database `{self.base_path + '/' + self.name if self.name else ''}` with "
            f"{self.database.get_number_of_documents()} indexed documents."
        )

    def initialize_remote_database(self) -> None:
        """Initializes a remote database."""
        raise NotImplementedError("Remote database is not implemented yet.")

    def add_documents(
        self, documents: list[Document], user: Optional[str] = None
    ) -> None:
        """Adds documents to an existing database.

        Documents must have metadata, and the metadata must have a `title` specified.
        Adding documents with the same title multiple times is not possible.

        Args:
            documents: A list of documents of type ``Document``.

            user: An optional string to identify a user.

        """
        # Check if database exists on disk. If not exit.
        if not self.database:
            raise DatabaseError(
                f"Tried to add documents to database `{self.base_path if self.base_path else ''+ '/' + self.name if self.name else ''}`, "
                "but this database does not exist."
            )

        # Validate metadata.
        if not self._validate_documents_metadata(documents=documents):
            raise MetadataError(
                "Tried to add documents with invalid metadata! Check if all documents have metadata and the field `title`."
            )

        # Add the documents.
        self.logger.info(
            f"Trying to add {len(documents)} documents to database at "
            f"`{self.base_path if self.base_path else '' + '/' + self.name if self.name else ''}`..."
        )

        if self.database.add_documents(documents, user):
            self.logger.info(
                "Added all documents to database. "
                f"Total number of documents in database: {self.database.get_number_of_documents()}",
            )
        else:
            self.logger.info(
                (
                    "Did not add documents to database, because documents with the title you "
                    "are trying to add already exist in the database."
                )
            )

    def delete_documents(self, title: str, user: Optional[str] = None) -> None:
        """Deletes all documents with the title ``title`` from the database.

        The title matching is case sensitive.

        Args:
            title: The title of the documents to be deleted.

            user: An optional string to identify a user.

        """
        if not self.database:
            raise DatabaseError(
                "Database does not exist. Please create it before running a query."
            )

        title = utils.remove_file_extension(title)

        if self.database.delete_documents(title, user):
            self.logger.info(f"Deleted documents with title `{title}` from database.")
        else:
            self.logger.info("Did not delete documents.")

    def query(self, query: str, user: Optional[str] = None) -> Optional[list[Document]]:
        """Query the database with a query.

        The instantiated database is queried with the given query string and returns
        a list of documents for a query.

        Args:
            query: A query as a string.

            user: An optional string to identify a user.

        Returns:
            A list of documents or None.

        """
        if not self.database:
            raise DatabaseError(
                "Database does not exist. Please create it before running a query."
            )

        return self.database.query(query, user)

    def _validate_documents_metadata(self, documents: list[Document]) -> bool:
        """Validate if document metadata exists and has the title key."""
        for document in documents:
            if (
                not document.metadata
                or not DataConstants.KEY_TITLE in document.metadata
            ):
                self.logger.debug("Metadata does not exist.")
                return False
        return True

    def _create_base_dir(self) -> None:
        """
        Helper to make sure database base dir exists.
        """
        if not self.base_path:
            return
        self.logger.info(f"Creating base dir for database `{self.base_path}` ...")
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
