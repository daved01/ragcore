from typing import Optional, Any
import yaml

from ragcore.app import AbstractApp
from ragcore.shared.constants import AppConstants, ConfigurationConstants
from ragcore.models.document_model import Document
from ragcore.services.document_service import DocumentService
from ragcore.services.database_service import DatabaseService
from ragcore.services.llm_service import LLMService


class RAGCore(AbstractApp):
    def __init__(
        self, config_path: Optional[str] = None, log_level="DEBUG", file_logging=False
    ):
        super().__init__(log_level, file_logging)
        self.database_service: Optional[DatabaseService] = None
        self.document_service: Optional[DocumentService] = None
        self.llm_service: Optional[LLMService] = None
        self.configuration: dict[str, dict[str, Any]] = self._get_config(
            config_file_path=config_path
            if config_path
            else AppConstants.DEFAULT_CONFIG_FILE_PATH
        )
        self._init_database_service()
        self._init_llm_service()

    def query(self, query: str) -> Optional[str]:
        """
        Query the database and make LLM request with the prompt and the context
        provided by the database.
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
        """
        Add a document to the database.
        The filename without the file extension is used as the title.
        """
        if not self.database_service:
            return

        self.document_service = DocumentService(self.logger)
        self.document_service.load_document(path=path)
        self.document_service.split_document(
            self.configuration[ConfigurationConstants.KEY_SPLITTER][
                ConfigurationConstants.KEY_CHUNK_SIZE
            ],
            self.configuration[ConfigurationConstants.KEY_SPLITTER][
                ConfigurationConstants.KEY_CHUNK_OVERLAP
            ],
        )
        self.database_service.add_documents(self.document_service.documents)

    def delete(self, title: str) -> None:
        """
        Deletes a collection from the database.
        A collection is a set of all documents with the same title.
        """
        if not title or not self.database_service:
            return

        self.database_service.delete_documents(title=title)

    def _init_llm_service(self):
        """
        Initialize LLM service.
        """
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
        """
        Creates a database or loads an existing one.
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
        """
        Gets the configuration from the configuration.yaml.
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
