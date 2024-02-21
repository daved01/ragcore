from typing import Optional, Any
import yaml

from ragcore.app.base_app import AbstractApp
from ragcore.shared.constants import AppConstants, ConfigurationConstants
from ragcore.models.app_model import QueryResponse, TitlesResponse
from ragcore.models.config_model import (
    AppConfiguration,
    DatabaseConfiguration,
    EmbeddingConfiguration,
    SplitterConfiguration,
    LLMConfiguration,
)
from ragcore.models.document_model import Document
from ragcore.services.document_service import DocumentService
from ragcore.services.database_service import DatabaseService
from ragcore.shared.errors import DatabaseError
from ragcore.services.llm_service import LLMService


class RAGCore(AbstractApp):
    """Retrieval-Augmented Generation Core lets you create RAG applications with a configuration and a few lines of code.

    RAGCore is a library that simplifies the implementation of Retrieval-Augmented Generation (RAG) applications.
    It combines a large language model with a knowledge store, allowing users to generate responses based on
    retrieved information.

    Usage:
        - Create an instance of RAGCore with the desired configuration.
        - Add documents to the knowledge store using the ``add_document`` method.
        - Query the system with natural language using the ``query`` method.
        - Retrieve generated responses.

    Example:
        .. code-block:: python

            # Instantiate RAGCore
            rag_instance = RAGCore(config_path='path/to/config.yaml')

            # Add a document to the knowledge store
            rag_instance.add(path='path/to/my_book.pdf')

            # Query the system
            query = 'Tell me about the topic.'
            response = rag_instance.query(query=query)

            # Print the content string of the generated response
            print(response.content)

            # List the document's titles and contents on which the response is based
            for doc in response.documents:
                print(doc.title, " | ", doc.content)

            # List all documents in the database
            print(rag_instance.get_titles())

            # Remove the document
            rag_instance.delete(title="my_book")

    Configuration:
        RAGCore relies on a configuration file (default name ``config.yaml``) to customize its behavior.
        For more information, refer to the `Configuration` section of the documentation at https://daved01.github.io/ragcore.

    Attributes:
       database_service: The service for handling database interactions.

       document_service: The service for handling document interactions.

       llm_service: The service for handling large language model interactions.

       configuration: An ``AppConfig`` containing the configuration.

    """

    def __init__(
        self, config: Optional[str] = None, log_level="DEBUG", file_logging=False
    ):
        """Initializer for RAGCore.

        Args:
            config: path to a configuration file. If not given, a file named `config.yaml` is expected in the root.
            log_level: The log level. Default value is `DEBUG`.
            file_logging: If `True`, logs are written to a file. Defaults to `False`.
        """
        super().__init__(log_level, file_logging)
        self.database_service: Optional[DatabaseService] = None
        self.document_service: Optional[DocumentService] = None
        self.llm_service: Optional[LLMService] = None
        self.configuration: AppConfiguration = self._get_config(
            config_file_path=config if config else AppConstants.DEFAULT_CONFIG_FILE_PATH
        )
        self._init_database_service()
        self._init_llm_service()

    def query(self, query: str, user: Optional[str] = None) -> QueryResponse:
        """Queries the database with a query.

        Queries the database and makes an LLM request with the prompt and the context
        provided by the database.

        Args:
            query: The query string to query the database with.

            user: An optional string to identify a user.

        Returns:
            A ``QueryResponse`` object. The field `content` contains the string or None if a response could not be generated.
            The field `documents` is a list with documents of type `Document` on which the response is based.

        """
        if not query or not self.database_service or not self.llm_service:
            return QueryResponse(content=None, documents=[], user=user)

        # Get relevant chunks from database.
        contexts: Optional[list[Document]] = self.database_service.query(query, user)

        if not contexts:
            print("Did not find documents in the database. Maybe it is empty?")
            return QueryResponse(content=None, documents=[], user=user)

        # Construct prompt from template and context.
        prompt: str = self.llm_service.create_prompt(query, contexts)

        # Query llm with prompt.
        content = self.llm_service.make_llm_request(prompt)
        return QueryResponse(content=content, documents=contexts, user=user)

    def add(self, path: str, user: Optional[str] = None) -> None:
        """Adds a document to the database.

        Adds the document in the path to the database. The filename, without the
        file extension, becomes the document title. For example, the path
        ``data/documents/my_book.pdf`` adds the book to the database with the title
        ``my_book``. Before it is added, the document is split into overlapping chunks
        as specified in the config file. Then, using the embedding model, vector
        representations are created which are then added to the database.

        Args:
            path: A string to the file location.

            user: An optional string to identify a user.

        """
        if not self.database_service:
            return

        self.document_service = DocumentService(self.logger)
        self.document_service.load_texts(path=path)
        self.document_service.split_pages(
            chunk_size=self.configuration.splitter_config.chunk_size,
            chunk_overlap=self.configuration.splitter_config.chunk_overlap,
        )
        self.database_service.add_documents(self.document_service.documents, user)

    def delete(self, title: str, user: Optional[str] = None) -> None:
        """Deletes a collection from the database.

        Given a title, all documents with that title, also called a collection, are
        deleted from the database.

        Args:
            title: The title of the collection to remove from the database.

            user: An optional string to identify a user.

        """
        if not title or not self.database_service:
            return

        self.database_service.delete_documents(title, user)

    def get_titles(self, user: Optional[str] = None) -> TitlesResponse:
        """Gets the document titles in the database.

        If a user identifier is given, the titles owned by this user are returned.
        If no user is given, the titles of the main collection are returned.
        The titles are sorted in alphabetical order.

        Args:
            user: An optional string to identify the owner.

        Returns:
            TitlesResponse: Object with an optional list of alphabetically sorted string titles and an optional user.

        """
        if not self.database_service:
            return TitlesResponse(user, [])

        titles = self.database_service.get_titles(user)

        return TitlesResponse(user=user, contents=titles)

    def _init_llm_service(self):
        """Initialize LLM service."""
        self.llm_service = LLMService(self.logger, config=self.configuration.llm_config)
        self.llm_service.initialize_llm()

    def _init_database_service(self) -> None:
        """Creates a database or loads an existing one.

        The database service requires both the database and embedding configurations, so that it can
        create embedding vectors.
        """
        self.database_service = DatabaseService(
            logger=self.logger,
            config=self.configuration.database_config,
            embedding_config=self.configuration.embedding_config,
        )

        # Initialize the database.
        if self.configuration.database_config.base_path:
            self.database_service.initialize_local_database()
        elif self.configuration.database_config.base_url:
            self.database_service.initialize_remote_database()
        else:
            raise DatabaseError(
                "Provide either a `base_dir` for a local database, or a `base_url` for a remote database."
            )

    def _get_config(self, config_file_path: str) -> AppConfiguration:
        """Gets the configuration from the ``config.yaml`` file.

        Loads the configuration from the file.

        Args:
            config_file_path: A string with the path to the config file.

        Returns:
            config: ``AppConfig`` with the configuration.
        """

        with open(config_file_path, "r", encoding="utf-8") as filehandler:
            config = yaml.load(filehandler, yaml.FullLoader)

        database_config_dict = config.get(ConfigurationConstants.KEY_DATABASE, {})
        splitter_config_dict = config.get(ConfigurationConstants.KEY_SPLITTER, {})
        embedding_config_dict = config.get(ConfigurationConstants.KEY_EMBEDDING, {})
        llm_config_dict = config.get(ConfigurationConstants.KEY_LLM, {})

        database_config = DatabaseConfiguration(
            provider=database_config_dict.get(
                ConfigurationConstants.KEY_DATABASE_PROVIDER, ""
            ),
            number_search_results=database_config_dict.get(
                ConfigurationConstants.KEY_NUMBER_SEARCH_RESULTS, -1
            ),
            base_path=database_config_dict.get(
                ConfigurationConstants.KEY_DATABASE_BASE_PATH
            ),
            base_url=database_config_dict.get(
                ConfigurationConstants.KEY_DATABASE_BASE_URL
            ),
        )
        splitter_config = SplitterConfiguration(
            chunk_overlap=splitter_config_dict.get(
                ConfigurationConstants.KEY_CHUNK_OVERLAP, -1
            ),
            chunk_size=splitter_config_dict.get(
                ConfigurationConstants.KEY_CHUNK_SIZE, -1
            ),
        )
        embedding_config = EmbeddingConfiguration(
            provider=embedding_config_dict.get(
                ConfigurationConstants.KEY_EMBEDDING_PROVIDER, ""
            ),
            model=embedding_config_dict.get(
                ConfigurationConstants.KEY_EMBEDDING_MODEL, ""
            ),
            endpoint=embedding_config_dict.get(
                ConfigurationConstants.KEY_AZURE_OPENAI_AZURE_ENDPOINT
            ),
            api_version=embedding_config_dict.get(
                ConfigurationConstants.KEY_AZURE_OPENAI_API_VERSION
            ),
        )
        llm_config = LLMConfiguration(
            provider=llm_config_dict.get(ConfigurationConstants.KEY_LLM_PROVIDER, ""),
            model=llm_config_dict.get(ConfigurationConstants.KEY_LLM_MODEL, ""),
            endpoint=llm_config_dict.get(
                ConfigurationConstants.KEY_AZURE_OPENAI_AZURE_ENDPOINT
            ),
            api_version=llm_config_dict.get(
                ConfigurationConstants.KEY_AZURE_OPENAI_API_VERSION
            ),
        )

        self.logger.info(f"Loaded config \n{config}\nfrom file `{config_file_path}`.")

        return AppConfiguration(
            database_config=database_config,
            splitter_config=splitter_config,
            embedding_config=embedding_config,
            llm_config=llm_config,
        )
