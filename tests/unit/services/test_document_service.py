import pytest

from docucite.services.document_service import DocumentService
from docucite.errors import UserConfigurationError
from tests import BaseTest
from tests.unit.services import DocuciteTestSetup


class TestDocumentService(BaseTest, DocuciteTestSetup):
    def test_load_document(self, mock_logger, mock_pages, mocker):
        class MockPDFLoader:
            def __init__(self, file_path):
                self.file_path = file_path

            def load_and_split(self):
                return mock_pages

        mocker.patch("docucite.services.document_service.PDFLoader", MockPDFLoader)

        document_service = DocumentService(mock_logger)
        assert not document_service.pages
        assert not document_service.documents

        document_service.load_document("some_path/file.pdf", "Greatest Book")

        assert len(document_service.pages) == 2
        assert document_service.pages[0] == mock_pages[0]
        assert document_service.pages[1] == mock_pages[1]
        assert "title" in document_service.pages[0].metadata
        assert "title" in document_service.pages[1].metadata

    def test_load_document_no_pages(self, mock_logger, mocker):
        class MockPDFLoader:
            def __init__(self, file_path):
                self.file_path = file_path

            def load_and_split(self):
                return []

        mocker.patch("docucite.services.document_service.PDFLoader", MockPDFLoader)

        document_service = DocumentService(mock_logger)
        assert not document_service.pages
        assert not document_service.documents

        document_service.load_document("some_path/file.pdf", "Greatest Book")

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
        document_service.split_document(split[0], split[1])
        assert len(document_service.documents) == expected_num_docs

    def test_split_document_no_docs(self, mock_logger):
        document_service = DocumentService(mock_logger)
        with pytest.raises(UserConfigurationError):
            document_service.split_document(10, 10)

    def test_documents_to_texts(self, mock_logger, mock_documents):
        document_service = DocumentService(logger=mock_logger)

        results = document_service.documents_to_texts(mock_documents)
        new_texts, new_metadatas = map(list, zip(*results))

        assert len(new_texts) == len(new_metadatas)
        assert new_texts[0] == mock_documents[0].page_content
        assert new_texts[1] == mock_documents[1].page_content
        assert new_metadatas[0] == mock_documents[0].metadata
        assert new_metadatas[1] == mock_documents[1].metadata
