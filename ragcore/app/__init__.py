from typing import Optional, Any
import yaml

from ragcore.app.base_app import AbstractApp
from ragcore.shared.constants import AppConstants, ConfigurationConstants
from ragcore.models.document_model import Document
from ragcore.services.document_service import DocumentService
from ragcore.services.database_service import DatabaseService
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

            # Print the generated response
            print(response)

            # Remove the document
            rag_instance.delete(title="my_book")

    Configuration:
        RAGCore relies on a configuration file (default name ``config.yaml``) to customize its behavior.
        For more information, refer to the `Configuration` section of the documentation at https://daved01.github.io/ragcore.

    Attributes:
       database_service: The service for handling database interactions.

       document_service: The service for handling document interactions.

       llm_service: The service for handling large language model interactions.

       configuration: A dict containing the configuration.

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
        self.configuration: dict[str, dict[str, Any]] = self._get_config(
            config_file_path=config if config else AppConstants.DEFAULT_CONFIG_FILE_PATH
        )
        self._init_database_service()
        self._init_llm_service()

    def query(self, query: str) -> Optional[str]:
        """Queries the database with a query.

        Queries the database and makes an LLM request with the prompt and the context
        provided by the database.

        Args:
            query: The query string to query the database with.

        Returns:
            A string with the response, or None if no answer could be generated.

        """
        if not query or not self.database_service or not self.llm_service:
            return None

        # Get relevant chunks from database.
        contexts: Optional[list[Document]] = self.database_service.query(query=query)

        if not contexts:
            print("Did not find documents in the database. Maybe it is empty?")
            return None

        # Construct prompt from template and context.
        prompt: str = self.llm_service.create_prompt(query, contexts)

        # Query llm with prompt.
        return self.llm_service.make_llm_request(prompt)

    def add(self, path: str) -> None:
        """Adds a document to the database.

        Adds the document in the path to the database. The filename, without the
        file extension, becomes the document title. For example, the path
        ``data/documents/my_book.pdf`` adds the book to the database with the title
        ``my_book``. Before it is added, the document is split into overlapping chunks
        as specified in the config file. Then, using the embedding model, vector
        representations are created which are then added to the database.

        Args:
            path: A string to the file location.

        """
        if not self.database_service:
            return

        self.document_service = DocumentService(self.logger)
        self.document_service.load_texts(path=path)
        self.document_service.split_pages(
            self.configuration[ConfigurationConstants.KEY_SPLITTER][
                ConfigurationConstants.KEY_CHUNK_SIZE
            ],
            self.configuration[ConfigurationConstants.KEY_SPLITTER][
                ConfigurationConstants.KEY_CHUNK_OVERLAP
            ],
        )
        self.database_service.add_documents(self.document_service.documents)

    def delete(self, title: str) -> None:
        """Deletes a collection from the database.

        Given a title, all documents with that title, also called a collection, are
        deleted from the database.

        Args:
            title: The title of the collection to remove from the database.

        """
        if not title or not self.database_service:
            return

        self.database_service.delete_documents(title=title)

    def _init_llm_service(self):
        """Initialize LLM service."""
        self.llm_service = LLMService(
            self.logger,
            llm_provider=self.configuration[ConfigurationConstants.KEY_LLM][
                ConfigurationConstants.KEY_LLM_PROVIDER
            ],
            llm_model=self.configuration[ConfigurationConstants.KEY_LLM][
                ConfigurationConstants.KEY_LLM_MODEL
            ],
            llm_config={
                ConfigurationConstants.KEY_AZURE_OPENAI_API_VERSION: self.configuration[
                    ConfigurationConstants.KEY_LLM
                ].get(ConfigurationConstants.KEY_AZURE_OPENAI_API_VERSION, ""),
                ConfigurationConstants.KEY_AZURE_OPENAI_AZURE_ENDPOINT: self.configuration[
                    ConfigurationConstants.KEY_LLM
                ].get(
                    ConfigurationConstants.KEY_AZURE_OPENAI_AZURE_ENDPOINT, ""
                ),
            },
        )
        self.llm_service.initialize_llm()

    def _init_database_service(self) -> None:
        """Creates a database or loads an existing one.

        The database name must be in the format <name>_<chunk_size>_<chunk_overlap>.
        """
        self.database_service = DatabaseService(
            logger=self.logger,
            base_path=self.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_DATABASE_BASE_PATH
            ],
            name=self.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_DATABASE_PROVIDER
            ]
            + "_"
            + str(
                self.configuration[ConfigurationConstants.KEY_SPLITTER][
                    ConfigurationConstants.KEY_CHUNK_SIZE
                ]
            )
            + "_"
            + str(
                self.configuration[ConfigurationConstants.KEY_SPLITTER][
                    ConfigurationConstants.KEY_CHUNK_OVERLAP
                ]
            ),
            num_search_results=self.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_NUMBER_SEARCH_RESULTS
            ],
            embedding_config=self.configuration[ConfigurationConstants.KEY_EMBEDDING],
        )

        # Initialize the database. If a base path is given in the configuration, we use a local
        # database. Otherwise, we initialize a remote database.
        if self.configuration[ConfigurationConstants.KEY_DATABASE].get(
            ConfigurationConstants.KEY_DATABASE_BASE_PATH
        ):
            self.database_service.initialize_local_database()
        else:
            self.database_service.initialize_remote_database()

    def _get_config(self, config_file_path: str) -> dict[str, dict[str, str | int]]:
        """Gets the configuration from the ``config.yaml`` file.

        Loads the configuration from the file.

        Args:
            config_file_path: A string with the path to the config file.
        """

        with open(config_file_path, "r", encoding="utf-8") as filehandler:
            config = yaml.load(filehandler, yaml.FullLoader)

        database_config = config.get(ConfigurationConstants.KEY_DATABASE, {})
        splitter_config = config.get(ConfigurationConstants.KEY_SPLITTER, {})
        embedding_config = config.get(ConfigurationConstants.KEY_EMBEDDING, {})
        llm_config = config.get(ConfigurationConstants.KEY_LLM, {})

        self.logger.info(f"Loaded config \n{config}\nfrom file `{config_file_path}`.")

        return {
            ConfigurationConstants.KEY_DATABASE: database_config,
            ConfigurationConstants.KEY_SPLITTER: splitter_config,
            ConfigurationConstants.KEY_EMBEDDING: embedding_config,
            ConfigurationConstants.KEY_LLM: llm_config,
        }
