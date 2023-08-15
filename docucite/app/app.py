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

from docucite.app import AbstractApp
from docucite.services.document_service import DocumentUploadService
from docucite.services.database_service import DatabaseService
from docucite.constants import AppConstants
from docucite.errors import DatabaseError


class DocuCiteApp(AbstractApp):
    def __init__(self, file_logging=False):
        super().__init__(file_logging)

    def run(self) -> None:
        self.logger.info("Setting up session ...")

        user_input = input(
            "Enter (n/N) for new document, any key to load existing one. "
        )

        database_service: DatabaseService = DatabaseService(
            logger=self.logger,
            database_name="chroma_200_50",
        )

        # Load database if exists or create it
        try:
            database_service.load_database()
        except DatabaseError:
            database_service.create_database()

        # Add documents
        if user_input.lower() == "n":
            title = input("Enter title of document: ")
            upload_service: DocumentUploadService = DocumentUploadService(self.logger)
            upload_service.load_document(
                path="data/Python summary.pdf", document_title=title
            )
            upload_service.split_document(200, 50)
            database_service.add_documents(upload_service.documents)

        # Run app
        self._run_event_loop()

    def _run_event_loop(self):
        """Main event loop for app"""
        print("Event loop started. Type 'quit' to exit.")
        while True:
            question = input("Enter your question (`quit` to exit): ")

            # Check for exit condition
            if question.lower() == "quit":
                print("Exiting...")
                break

            # TODO: Query model
