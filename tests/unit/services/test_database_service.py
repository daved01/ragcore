import os
import pytest
from langchain.vectorstores import Chroma
from langchain.schema.document import Document
from langchain.embeddings import OpenAIEmbeddings

from docucite.constants import AppConstants
from docucite.services.database_service import DatabaseService
from docucite.errors import DatabaseError, MissingMetadataError, InvalidMetadataError
from tests import BaseTest
from tests.unit.services import DocuciteTestSetup


class TestDatabaseService(BaseTest, DocuciteTestSetup):
    def test_create_database_database_exists(self, mock_logger, mocker):
        with pytest.raises(DatabaseError):
            db_service = DatabaseService(mock_logger, "database_already_exists")

            mocker.patch.object(db_service, "_dir_exists", return_value=True)

            db_service.create_database()

    def test_create_database_base_folder_exists(self, mock_logger, mocker):
        # If
        db_service = DatabaseService(logger=mock_logger, database_name=None)
        mocker.patch.object(db_service, "_dir_exists", side_effect=[False, True])
        makedirs_mock = mocker.patch("os.makedirs", return_value=None)

        # When
        db_service.create_database()

        # Then
        assert db_service.vectordb is not None
        assert isinstance(db_service.vectordb.embeddings, OpenAIEmbeddings)
        makedirs_mock.assert_not_called()

    def test_create_database_base_folder_not_exists(self, mock_logger, mocker):
        # If
        db_service = DatabaseService(logger=mock_logger, database_name=None)
        mocker.patch.object(db_service, "_dir_exists", side_effect=[False, False])
        mocker.patch("os.path.exists", return_value=False)
        makedirs_mock = mocker.patch("os.makedirs", return_value=None)

        # When
        db_service.create_database()

        # Then
        assert db_service.vectordb is not None
        assert isinstance(db_service.vectordb.embeddings, OpenAIEmbeddings)
        assert (
            makedirs_mock.call_count == 2
        )  # langchain Chroma dependency calls os.makedirs() too
        makedirs_mock.assert_any_call(AppConstants.DATABASE_BASE_DIR)

    def test_update_database(
        self, mock_logger, mock_documents, mock_documents_best_book
    ):
        # Create database in memory with the mock_documents
        db_service = DatabaseService(logger=mock_logger, database_name=None)

        db_service.vectordb = Chroma.from_documents(
            mock_documents_best_book,
            db_service.embedding,
            persist_directory=db_service.database_path,
        )

        ids_first_docs = db_service.vectordb.get().get("ids")

        # When
        db_service.add_documents(mock_documents)

        # Then
        ids_second_docs = db_service.vectordb.get().get("ids")
        assert len(ids_first_docs) == 1
        assert len(ids_second_docs) == 3
        assert ids_first_docs[0] in ids_second_docs

    def test_search(self, mock_logger, mocker, mock_documents):
        class MockVectorDB:
            def __init__(self):
                pass

            def similarity_search(self, query, k):
                return mock_documents

        mocker.patch("docucite.services.database_service.Chroma", MockVectorDB)
        db_service = DatabaseService(logger=mock_logger, database_name=None)
        db_service.vectordb = MockVectorDB()
        res = db_service.search("What is a good question?")
        assert len(res) == 2
        assert isinstance(res[0], Document)

    def test_search_database_empty(self, mock_logger, mocker):
        class MockVectorDB:
            def __init__(self):
                pass

            def similarity_search(self, query, k):
                return []

        mocker.patch("docucite.services.database_service.Chroma", MockVectorDB)
        db_service = DatabaseService(logger=mock_logger, database_name=None)
        db_service.vectordb = MockVectorDB()
        res = db_service.search("What is a good question?")
        assert len(res) == 0

    def test_search_no_database(self, mock_logger):
        db_service = DatabaseService(logger=mock_logger, database_name=None)
        with pytest.raises(DatabaseError):
            db_service.search("Why does this fail?")

    # All is good if no error is raised
    def test_validate_documents_metadata_pass(
        self, mock_logger, mock_three_texts, mock_three_metadatas
    ):
        db_service = DatabaseService(logger=mock_logger, database_name=None)
        db_service._validate_documents_metadata(
            texts=mock_three_texts, metadatas=mock_three_metadatas
        )

    def test_validate_documents_metadata_missing_metadata(
        self, mock_logger, mock_three_texts
    ):
        with pytest.raises(MissingMetadataError):
            db_service = DatabaseService(logger=mock_logger, database_name=None)
            db_service._validate_documents_metadata(
                texts=mock_three_texts, metadatas=[]
            )

    def test_validate_documents_metadata_one_metadata_missing(
        self, mock_logger, mock_three_texts, mock_two_metadatas
    ):
        with pytest.raises(MissingMetadataError):
            db_service = DatabaseService(logger=mock_logger, database_name=None)
            db_service._validate_documents_metadata(
                texts=mock_three_texts, metadatas=mock_two_metadatas
            )

    def test_validate_documents_metadata_metadata_missing_title(
        self, mock_logger, mock_three_texts, mock_three_metadatas_one_missing_title
    ):
        with pytest.raises(InvalidMetadataError):
            db_service = DatabaseService(logger=mock_logger, database_name=None)
            db_service._validate_documents_metadata(
                texts=mock_three_texts, metadatas=mock_three_metadatas_one_missing_title
            )

    # TODO: Flaky
    def test_validate_documents_not_in_database_pass(
        self, mock_logger, mock_documents, mock_three_metadatas
    ):
        # Create in memory database from mock_documents
        db_service = DatabaseService(logger=mock_logger, database_name=None)
        db_service.vectordb = Chroma.from_documents(
            mock_documents,
            db_service.embedding,
            persist_directory=db_service.database_path,
        )

        db_service._validate_documents_not_in_database(metadatas=mock_three_metadatas)

    def test_validate_documents_not_in_database_fail(self, mock_logger, mock_documents):
        metadatas = [{"page": 6, "title": "Greatest book"}]
        with pytest.raises(DatabaseError):
            db_service = DatabaseService(logger=mock_logger, database_name=None)
            db_service.vectordb = Chroma.from_documents(
                mock_documents,
                db_service.embedding,
                persist_directory=db_service.database_path,
            )

            db_service._validate_documents_not_in_database(metadatas=metadatas)

    def test_update_database_not_exist(self, mock_logger, mock_documents):
        with pytest.raises(DatabaseError):
            db_service = DatabaseService(mock_logger, "database_does_not_exist")
            db_service.add_documents(mock_documents)

    def test_create_base_dir(self, mock_logger):
        db_service = DatabaseService(mock_logger, "")
        db_service._create_base_dir()

        assert os.path.exists(AppConstants.DATABASE_BASE_DIR)

    def test_create_base_dir_exist(self, mock_logger, mocker):
        mocker.patch("os.path.exists", return_value=True)
        makedirs_spy = mocker.spy(os, "makedirs")

        db_service = DatabaseService(mock_logger, "")
        db_service._create_base_dir()

        makedirs_spy.assert_not_called()
