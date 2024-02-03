import pytest

from ragcore.services.document_service import DocumentService
from ragcore.shared.errors import UserConfigurationError
from tests import BaseTest
from tests.unit.services import RAGCoreTestSetup


class TestDocumentService(BaseTest, RAGCoreTestSetup):
    def test_load_document(self, mock_logger, mock_pages, mocker):
        class MockPDFLoader:
            def __init__(self, file_path):
                self.file_path = file_path

            def load_and_split(self, title):
                for page in mock_pages:
                    page.metadata["title"] = title
                return mock_pages

        mocker.patch("ragcore.services.document_service.PDFLoader", MockPDFLoader)

        document_service = DocumentService(mock_logger)
        assert not document_service.pages
        assert not document_service.documents

        document_service.load_texts("some_path/Greatest_Book.pdf")

        assert len(document_service.pages) == 2
        assert document_service.pages[0] == mock_pages[0]
        assert document_service.pages[1] == mock_pages[1]
        assert "title" in document_service.pages[0].metadata
        assert "title" in document_service.pages[1].metadata

    def test_load_document_no_pages(self, mock_logger, mocker):
        class MockPDFLoader:
            def __init__(self, file_path):
                self.file_path = file_path

            def load_and_split(self, title):
                return []

        mocker.patch("ragcore.services.document_service.PDFLoader", MockPDFLoader)

        document_service = DocumentService(mock_logger)
        assert not document_service.pages
        assert not document_service.documents

        document_service.load_texts("some_path/Greatest_Book.pdf")

        assert len(document_service.pages) == 0

    @pytest.mark.parametrize(
        "split, expected_num_docs",
        [((1000, 200), 2), ((50, 10), 6), ((106, 10), 3), ((10, 4), 28), ((50, 0), 6)],
    )
    def test_split_document(
        self, mock_logger, mock_documents, expected_document, split, expected_num_docs
    ):
        document_service = DocumentService(mock_logger)

        document_service.pages = list(mock_documents)

        # Check pages
        assert len(document_service.pages) == 2
        assert expected_document in document_service.pages

        # Check documents
        assert len(document_service.documents) == 0

        # Split documents
        document_service.split_pages(split[0], split[1])
        assert len(document_service.documents) == expected_num_docs

    def test_split_document_no_docs(self, mock_logger):
        document_service = DocumentService(mock_logger)
        with pytest.raises(UserConfigurationError):
            document_service.split_pages(10, 10)
