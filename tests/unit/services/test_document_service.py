import pytest
from unittest.mock import patch

from docucite.services.document_service import DocumentUploadService, DocumentService
from docucite.errors import UserConfigurationError
from tests import BaseTest
from tests.unit.services import DocuciteTestSetup


class TestDocumentService(BaseTest, DocuciteTestSetup):
    def test_documents_to_texts(self, mock_logger, mock_documents):
        document_service = DocumentService(logger=mock_logger)

        results = document_service.documents_to_texts(mock_documents)
        new_texts, new_metadatas = map(list, zip(*results))

        assert len(new_texts) == len(new_metadatas)
        assert new_texts[0] == mock_documents[0].page_content
        assert new_texts[1] == mock_documents[1].page_content
        assert new_metadatas[0] == mock_documents[0].metadata
        assert new_metadatas[1] == mock_documents[1].metadata


class TestDocumentUploadService(BaseTest, DocuciteTestSetup):
    def test_load_document(self):
        raise NotImplementedError

    @pytest.mark.parametrize(
        "split, expected_num_docs",
        [((1000, 200), 2), ((50, 10), 5), ((106, 10), 3), ((10, 4), 27), ((50, 0), 5)],
    )
    def test_split_document(
        self, mocker, mock_documents, expected_document, split, expected_num_docs
    ):
        mock_logger = mocker.patch("logging.getLogger")
        mock_logger_instance = mock_logger.return_value
        mock_logger_instance.info = mocker.MagicMock()
        document_service = DocumentUploadService(mock_logger)

        document_service.pages = list(mock_documents)

        # Check pages
        assert len(document_service.pages) == 2
        assert expected_document in document_service.pages

        # Check documents
        assert len(document_service.documents) == 0

        # Split documents
        document_service.split_document(split[0], split[1])
        assert len(document_service.documents) == expected_num_docs

    def test_split_document_no_docs(self, mocker):
        mock_logger = mocker.patch("logging.getLogger")
        mock_logger_instance = mock_logger.return_value
        mock_logger_instance.info = mocker.MagicMock()
        document_service = DocumentUploadService(mock_logger)
        with pytest.raises(UserConfigurationError):
            document_service.split_document(10, 10)


class TestDocumentRetrievalService:
    def test_retrieve_documents(self):
        raise NotImplementedError

    def test_get_docs_similarity_search(self):
        raise NotImplementedError

    def test_document_to_str(self):
        raise NotImplementedError
