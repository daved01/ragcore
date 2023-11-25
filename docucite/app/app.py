from typing import Optional, Any
import yaml

from docucite.app import AbstractApp
from docucite.constants import AppConstants, ConfigurationConstants
from docucite.errors import DatabaseError, UserConfigurationError
from docucite.models.document_model import Document
from docucite.services.document_service import DocumentService
from docucite.services.database_service import DatabaseService
from docucite.services.llm_service import LLMService


class DocuCiteApp(AbstractApp):
    def __init__(self, file_logging=False):
        super().__init__(file_logging)
        self.database_service: Optional[DatabaseService] = None
        self.document_service: Optional[DocumentService] = None
        self.llm_service: Optional[LLMService] = None
        self.configuration: dict[str, Any] = self._get_config()

    def run(self) -> None:
        self.logger.info("Setting up session ...")

        user_input = input(
            "Enter (n/N) for new document, any key to load existing one. "
        )

        # Create database or load existing one
        self.init_database_service()

        if not self.database_service:
            return

        # Add documents
        if user_input.lower() == "n":
            title = input("Enter title of document: ")
            self.document_service = DocumentService(self.logger)
            self.document_service.load_document(
                path=AppConstants.DOCUMENT_BASE_PATH
                + self.configuration[ConfigurationConstants.KEY_DOCUMENT],
                document_title=title,
            )
            self.document_service.split_document(
                self.configuration[ConfigurationConstants.KEY_CHUNK_SIZE],
                self.configuration[ConfigurationConstants.KEY_CHUNK_OVERLAP],
            )
            self.database_service.add_documents(self.document_service.documents)

        # Initialize LLMService
        self.llm_service = LLMService(self.logger)
        self.llm_service.initialize_llm()

        # Run app
        self._run_event_loop()

    def init_database_service(self) -> None:
        """
        Creates a database or loads an existing one.
        The database name must be in the format <name>_<chunk_size>_<chunk_overlap>.
        """
        self.database_service = DatabaseService(
            logger=self.logger,
            database_name=self.configuration[ConfigurationConstants.KEY_DATABASE_NAME]
            + "_"
            + str(self.configuration[ConfigurationConstants.KEY_CHUNK_SIZE])
            + "_"
            + str(self.configuration[ConfigurationConstants.KEY_CHUNK_OVERLAP]),
        )

        # Load database if exists or create it
        try:
            self.database_service.load_database()
        except DatabaseError:
            self.database_service.create_database()

    def _run_event_loop(self):
        """Main event loop for CLI app"""
        print("\nEvent loop started. Type `quit` to exit.\n")
        while True:
            question = input("Enter your question (`quit` to exit): ")

            # Check for exit condition
            if question.lower() == "quit":
                print("Exiting ...")
                break

            # Get relevant chunks from database
            contexts: list[Document] = self.database_service.search(query=question)

            # Construct prompt from template and context
            prompt: str = self.llm_service.create_prompt(question, contexts)

            # Query llm with prompt
            response: str = self.llm_service.make_llm_request(prompt)

            # Show response
            separator_line = "--" * 64
            print(f"\n{separator_line}\n{response}\n{separator_line}\n")

    def _get_config(self) -> dict[str, str | int]:
        """
        Gets the configuration from the configuration.yaml file in the root.
        If the file is not present or incomplete, a default configuration is used instead,
        with the exception of a document name which must be provided.
        """
        with open(
            ConfigurationConstants.CONFIG_FILE_PATH, "r", encoding="utf-8"
        ) as filehandler:
            config = yaml.load(filehandler, yaml.FullLoader)
        database_name = config.get(
            ConfigurationConstants.KEY_DATABASE_NAME,
            ConfigurationConstants.DEFAULT_DATABASE_NAME,
        )

        document = config.get(ConfigurationConstants.KEY_DOCUMENT)

        if not document:
            raise UserConfigurationError(
                f"A document to load must be provided in the configuration "
                f"file under the key `{ConfigurationConstants.KEY_DOCUMENT}`.",
            )

        chunk_size = config.get(
            ConfigurationConstants.KEY_CHUNK_SIZE,
            ConfigurationConstants.DEFAULT_CHUNK_SIZE,
        )
        chunk_overlap = config.get(
            ConfigurationConstants.KEY_CHUNK_OVERLAP,
            ConfigurationConstants.DEFAULT_CHUNK_OVERLAP,
        )

        self.logger.info(
            f"Loaded config `{config}` from file `{ConfigurationConstants.CONFIG_FILE_PATH}`."
        )

        return {
            ConfigurationConstants.KEY_DATABASE_NAME: database_name,
            ConfigurationConstants.KEY_DOCUMENT: document,
            ConfigurationConstants.KEY_CHUNK_SIZE: int(chunk_size),
            ConfigurationConstants.KEY_CHUNK_OVERLAP: int(chunk_overlap),
        }
