from typing import Optional, Any
import yaml

from docucite.app import AbstractApp
from docucite.constants import AppConstants, ConfigurationConstants
from docucite.models.document_model import Document
from docucite.services.document_service import DocumentService
from docucite.services.database_service import DatabaseService
from docucite.services.llm_service import LLMService


class DocuCiteApp(AbstractApp):
    def __init__(self, config_path: Optional[str] = None, file_logging=False):
        super().__init__(file_logging)
        self.database_service: Optional[DatabaseService] = None
        self.document_service: Optional[DocumentService] = None
        self.llm_service: Optional[LLMService] = None
        self.configuration: dict[str, dict[str, Any]] = self._get_config(
            config_file_path=config_path
            if config_path
            else AppConstants.DEFAULT_CONFIG_FILE_PATH
        )

    def run(self) -> None:
        self.logger.info("Setting up session ...")

        # Create database or load existing one.
        self.init_database_service()

        if not self.database_service:
            return

        user_input = input(
            "Enter (n/N) for new document, any key to load existing one. "
        )

        # Add documents.
        if user_input.lower() == "n":
            title = input("Enter title of document: ")
            self.document_service = DocumentService(self.logger)
            self.document_service.load_document(
                path=self.configuration[ConfigurationConstants.KEY_DATABASE][
                    ConfigurationConstants.KEY_DOCUMENT_BASE_PATH
                ]
                + "/"
                + title,
                document_title=title,
            )
            self.document_service.split_document(
                self.configuration[ConfigurationConstants.KEY_SPLITTER][
                    ConfigurationConstants.KEY_CHUNK_SIZE
                ],
                self.configuration[ConfigurationConstants.KEY_SPLITTER][
                    ConfigurationConstants.KEY_CHUNK_OVERLAP
                ],
            )

            self.database_service.add_documents(self.document_service.documents)

        # Initialize LLMService.
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

        # Run app.
        self._run_event_loop()

    def init_database_service(self) -> None:
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
            embedding_provider=self.configuration[ConfigurationConstants.KEY_EMBEDDING][
                ConfigurationConstants.KEY_EMBEDDING_PROVIDER
            ],
            embedding_model=self.configuration[ConfigurationConstants.KEY_EMBEDDING][
                ConfigurationConstants.KEY_EMBEDDING_MODEL
            ],
        )

        # Initialize the database. If a base path is given in the configuration, we use a local
        # database. Otherwise, we initialize a remote database.
        if self.configuration[ConfigurationConstants.KEY_DATABASE].get(
            ConfigurationConstants.KEY_DATABASE_BASE_PATH
        ):
            self.database_service.initialize_local_database()
        else:
            self.database_service.initialize_remote_database()

    def _run_event_loop(self):
        """Main event loop for CLI app"""
        print("\nEvent loop started. Type `quit` to exit.\n")
        while True:
            question = input("Enter your question (`quit` to exit): ")

            # Check for exit condition.
            if question.lower() == "quit":
                print("Exiting ...")
                break

            # Get relevant chunks from database.
            contexts: list[Document] = self.database_service.query(query=question)

            # Construct prompt from template and context.
            prompt: str = self.llm_service.create_prompt(question, contexts)

            # Query llm with prompt.
            response: str = self.llm_service.make_llm_request(prompt)

            # Show response.
            separator_line = "--" * 64
            print(f"\n{separator_line}\n{response}\n{separator_line}\n")

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
