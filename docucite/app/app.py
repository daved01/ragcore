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


class DocuCiteApp(AbstractApp):
    def __init__(self, file_logging=False):
        super().__init__(file_logging)

    def run(self) -> None:
        self.logger.info("Setting up session ...")

        upload_documents = input(
            "Enter (n/N) for new document, any key to load existing one. "
        )

        title = None
        upload_doc = False

        database_service: DatabaseService = DatabaseService(
            logger=self.logger,
            database_name="chroma_200_50",
        )

        # TODO: Try to load database

        # If exists: Load database
        # If not exists: Create database

        # Add documents

        if upload_documents.lower() == "n":
            upload_doc = True
            title = input("Enter title of document: ")
            upload_service: DocumentUploadService = DocumentUploadService(self.logger)
            upload_service.load_document(
                path="data/Python summary.pdf", document_title=title
            )
            upload_service.split_document(1500, 150)
            database_service.create_database(upload_service.documents)
        else:
            database_service.load_database()
            print(
                database_service.vectordb.similarity_search("What about asyncio?", k=4)
            )
            return

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
