from langchain.schema.document import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import os
import shutil
import pytest
from unittest.mock import MagicMock

from docucite.constants import AppConstants
from docucite.services.database_service import DatabaseService
from docucite.errors import DatabaseError
from docucite.services import database_service as db_service
from tests import BaseTest
from tests.unit.services import DocuciteTestSetup


class TestDatabaseService(BaseTest, DocuciteTestSetup):
    @pytest.fixture
    def remove_folder(self, request):
        folder_path = AppConstants.DATABASE_BASE_DIR + "/" + "database_already_exists"

        # os.makedirs(folder_path)
        def cleanup():
            shutil.rmtree(folder_path)

        request.addfinalizer(cleanup)
        return folder_path

    @pytest.fixture
    def mock_dir_exists(self, monkeypatch):
        def mock_dir_exists_method(self, path: str):
            if path == AppConstants.DATABASE_BASE_DIR:
                return True
            else:
                return False

        monkeypatch.setattr(
            db_service.DatabaseService,
            "_dir_exists",
            mock_dir_exists_method,
        )

    def test_create_database_database_exists(
        self, mock_logger, mock_documents, remove_folder
    ):
        # Base folder and database exist.
        database_name = "database_already_exists"

        with pytest.raises(DatabaseError):
            db_service = DatabaseService(mock_logger, database_name)
            db_service.create_database(mock_documents)

    def test_create_database_base_folder_exists(
        self, mock_logger, mock_documents, mock_dir_exists
    ):
        # Base folder exists, database does not exist.
        db_service = DatabaseService(logger=mock_logger, database_name=None)

        # When
        db_service.create_database(mock_documents)

        # Then
        # Perform basic search on this DB. Depends on embedding and docs.
        assert db_service.vectordb != None
        assert type(db_service.vectordb.embeddings) == OpenAIEmbeddings
        assert (
            db_service.vectordb.similarity_search("What a question here?", k=2) != None
        )

    def test_create_database_base_folder_not_exists(
        self, mock_logger, mock_documents, mocker
    ):
        db_service = DatabaseService(
            logger=mock_logger, database_name="db_missing_base_folder"
        )

        mock_db_service = MagicMock()

        def mock_dir_exists(path: str):
            if path == AppConstants.DATABASE_BASE_DIR:
                return False
            elif (
                path == AppConstants.DATABASE_BASE_DIR + "/" + "db_missing_base_folder"
            ):
                return False
            else:
                True

        mock_create_base_dir = MagicMock()

        mock_db_service.side_effect = mock_dir_exists
        db_service._dir_exists = mock_dir_exists
        db_service._create_base_dir = mock_create_base_dir

        # When
        db_service.create_database(mock_documents)

        # Then
        mock_create_base_dir.assert_called_once()

    def test_update_database(
        self, mock_logger, mock_documents, mock_documents_best_book
    ):
        # Create database in memory with the mock_documents
        database_path = None
        db_service = DatabaseService(logger=mock_logger, database_name=None)

        db_service.vectordb = Chroma.from_documents(
            mock_documents_best_book,
            db_service.embedding,
            persist_directory=db_service.database_path,
        )

        ids_first_docs = db_service.vectordb.get().get("ids")

        # When
        db_service.update_database(mock_documents)

        # Then
        ids_second_docs = db_service.vectordb.get().get("ids")
        assert len(ids_first_docs) == 1
        assert len(ids_second_docs) == 3
        assert ids_first_docs[0] in ids_second_docs

    def test_update_database_not_exist(self, mock_logger, mock_documents):
        with pytest.raises(DatabaseError):
            db_service = DatabaseService(mock_logger, "database_does_not_exist")
            db_service.update_database(mock_documents)

    def test_create_base_dir(self, mock_logger, tmpdir):
        db_service = DatabaseService(mock_logger, "")
        db_service._create_base_dir()

        assert os.path.exists(AppConstants.DATABASE_BASE_DIR)

    def test_create_base_dir_exist(self, mock_logger, tmpdir, mocker):
        mocker.patch("os.path.exists", return_value=True)
        makedirs_spy = mocker.spy(os, "makedirs")

        db_service = DatabaseService(mock_logger, "")
        db_service._create_base_dir()

        makedirs_spy.assert_not_called()
