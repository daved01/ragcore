"""
Entry point for requests coming from the front-end.
Handles: routing, authentication, request validation, error handling
Communicates with the service layer.

Accepts:
- question
- Command to upload new document
- Command to delete database
- Settings

Returns:
- result
- Confirmations
"""
from typing import Optional
from langchain.schema.document import Document

from docucite.app import AbstractApp
from docucite.services.document_service import DocumentService
from docucite.services.database_service import DatabaseService
from docucite.errors import DatabaseError
from docucite.services.llm_service import LLMService


class DocuCiteApp(AbstractApp):
    def __init__(self, file_logging=False):
        super().__init__(file_logging)
        self.database_service: Optional[DatabaseService] = None
        self.document_service: Optional[DocumentService] = None
        self.llm_service: Optional[LLMService] = None

    def run(self) -> None:
        self.logger.info("Setting up session ...")

        user_input = input(
            "Enter (n/N) for new document, any key to load existing one. "
        )

        self.database_service = DatabaseService(
            logger=self.logger,
            database_name="chroma_200_50",
        )

        # Load database if exists or create it
        try:
            self.database_service.load_database()
        except DatabaseError:
            self.database_service.create_database()

        # Add documents
        if user_input.lower() == "n":
            title = input("Enter title of document: ")
            self.document_service = DocumentService(self.logger)
            self.document_service.load_document(
                path="data/Python summary.pdf", document_title=title
            )
            self.document_service.split_document(200, 50)
            self.database_service.add_documents(self.document_service.documents)

        # Initialize LLMService here, only when rest is available
        self.llm_service = LLMService(self.logger)
        self.llm_service.initialize_llm()

        # Run app
        self._run_event_loop()

    def _run_event_loop(self):
        """Main event loop for app"""
        print("\nEvent loop started. Type 'quit' to exit.\n")
        while True:
            question = input("Enter your question (`quit` to exit): ")

            # Check for exit condition
            if question.lower() == "quit":
                print("Exiting ...")
                break

            contexts: list[Document] = self.database_service.search(query=question)

            # Construct prompt from template and context
            prompt: str = self.llm_service.create_prompt(question, contexts)

            # Query llm with prompt
            response: str = self.llm_service.make_llm_request(prompt)  # Query llm

            # Show response
            print("--" * 32)
            print(f"\n{response}\n")
            print("--" * 32)
            print("")
