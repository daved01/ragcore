import pytest

from docucite.shared.errors import EmbeddingError, DatabaseError, MetadataError
from docucite.models.database_model import ChromaDatabase
from docucite.models.embedding_model import BaseEmbedding
from docucite.services.database_service import DatabaseService
from tests import BaseTest
from tests.unit.services import DocuciteTestSetup


class TestDatabaseService(BaseTest, DocuciteTestSetup):
    def test_init_embedding_openai(
        self, mocker, mock_logger, mock_config, mock_openai_embedding
    ):
        mocker.patch("docucite.models.embedding_model.OpenAI", mock_openai_embedding)
        database_service = DatabaseService(
            logger=mock_logger,
            base_path=mock_config["path"],
            name=mock_config["name"],
            num_search_results=mock_config["num_search_res"],
            embedding_provider="openai",
            embedding_model=mock_config["embedding_model"],
        )
        assert isinstance(database_service.embedding.client, mock_openai_embedding)

    def test_init_embedding_invalid_provider(
        self,
        mock_logger,
        mock_config,
    ):
        with pytest.raises(EmbeddingError):
            _ = DatabaseService(
                logger=mock_logger,
                base_path=mock_config["path"],
                name=mock_config["name"],
                num_search_results=mock_config["num_search_res"],
                embedding_provider="not-supported",
                embedding_model=mock_config["embedding_model"],
            )

    def test_initialize_local_database(
        self, mocker, mock_logger, mock_config, mock_openai_embedding
    ):
        mock_database = mocker.Mock()
        mocker.patch("docucite.models.database_model.ChromaDatabase", mock_database)
        mocker.patch("docucite.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            base_path=mock_config["path"],
            name="chroma",
            num_search_results=mock_config["num_search_res"],
            embedding_provider="openai",
            embedding_model=mock_config["embedding_model"],
        )

        database_service.initialize_local_database()

        assert mock_makedirs.call_count == 1
        assert mock_chroma_db_client.call_count == 1
        assert database_service.base_path == "path"
        assert database_service.name == "chroma"
        assert database_service.number_search_results == 2
        assert isinstance(database_service.embedding, BaseEmbedding)

    def test_initialize_local_database_not_supported_database_name(
        self, mocker, mock_logger, mock_config, mock_openai_embedding
    ):
        mock_database = mocker.Mock()
        mocker.patch("docucite.models.database_model.ChromaDatabase", mock_database)
        mocker.patch("docucite.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")
        database_service = DatabaseService(
            logger=mock_logger,
            base_path=mock_config["path"],
            name="not_supported",
            num_search_results=mock_config["num_search_res"],
            embedding_provider="openai",
            embedding_model=mock_config["embedding_model"],
        )
        with pytest.raises(DatabaseError):
            database_service.initialize_local_database()

    def test_add_documents(
        self, mocker, mock_logger, mock_config, mock_openai_embedding, mock_documents
    ):
        mock_add_docs = mocker.Mock()
        mock_database_class = mocker.patch(
            "docucite.models.database_model.ChromaDatabase"
        )
        mock_database_instance = mock_database_class.return_value
        mock_database_instance.add_documents = mock_add_docs
        mock_database_add_documents = mocker.patch(
            "docucite.services.database_service.ChromaDatabase.add_documents",
            mock_add_docs,
        )
        mocker.patch("docucite.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            base_path=mock_config["path"],
            name="chroma",
            num_search_results=mock_config["num_search_res"],
            embedding_provider="openai",
            embedding_model=mock_config["embedding_model"],
        )

        database_service.initialize_local_database()
        database_service.add_documents(documents=mock_documents)

        assert isinstance(database_service.database, ChromaDatabase)
        assert mock_database_add_documents.call_count == 1

    def test_add_documents_database_not_exist(
        self, mocker, mock_logger, mock_config, mock_openai_embedding, mock_documents
    ):
        mocker.patch("docucite.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            base_path=mock_config["path"],
            name="chroma",
            num_search_results=mock_config["num_search_res"],
            embedding_provider="openai",
            embedding_model=mock_config["embedding_model"],
        )
        with pytest.raises(DatabaseError):
            database_service.add_documents(mock_documents)

    def test_add_documents_metadata_title_missing(
        self,
        mocker,
        mock_logger,
        mock_config,
        mock_openai_embedding,
        mock_documents_metadata_title_missing,
    ):
        mock_database = mocker.Mock()
        mocker.patch("docucite.models.database_model.ChromaDatabase", mock_database)
        mocker.patch("docucite.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            base_path=mock_config["path"],
            name="chroma",
            num_search_results=mock_config["num_search_res"],
            embedding_provider="openai",
            embedding_model=mock_config["embedding_model"],
        )
        database_service.initialize_local_database()
        with pytest.raises(MetadataError):
            database_service.add_documents(mock_documents_metadata_title_missing)

    def test_add_documents_metadata_missing(
        self,
        mocker,
        mock_logger,
        mock_config,
        mock_openai_embedding,
        mock_documents_missing_metadata,
    ):
        mock_database = mocker.Mock()
        mocker.patch("docucite.models.database_model.ChromaDatabase", mock_database)
        mocker.patch("docucite.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            base_path=mock_config["path"],
            name="chroma",
            num_search_results=mock_config["num_search_res"],
            embedding_provider="openai",
            embedding_model=mock_config["embedding_model"],
        )
        database_service.initialize_local_database()
        with pytest.raises(MetadataError):
            database_service.add_documents(mock_documents_missing_metadata)

    def test_query(self, mocker, mock_logger, mock_config, mock_documents):
        mock_database = mocker.Mock()
        mocker.patch("docucite.models.database_model.ChromaDatabase", mock_database)
        mocker.patch(
            "docucite.services.database_service.DatabaseService.query",
            return_value="Hello",
        )
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            base_path=mock_config["path"],
            name="chroma",
            num_search_results=mock_config["num_search_res"],
            embedding_provider="openai",
            embedding_model=mock_config["embedding_model"],
        )
        database_service.initialize_local_database()
        response = database_service.query("my_query")

        assert response == "Hello"

    def test_query_fail(self, mocker, mock_logger, mock_config, mock_documents):
        mock_database = mocker.Mock()
        mocker.patch("docucite.models.database_model.ChromaDatabase", mock_database)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            base_path=mock_config["path"],
            name="chroma",
            num_search_results=mock_config["num_search_res"],
            embedding_provider="openai",
            embedding_model=mock_config["embedding_model"],
        )
        with pytest.raises(DatabaseError):
            database_service.query("my_query")

    def test_create_base_dir(self, mocker, mock_logger, mock_config):
        base_path = "/path/to/base"
        database_service = DatabaseService(
            logger=mock_logger,
            base_path=base_path,
            name="chroma",
            num_search_results=mock_config["num_search_res"],
            embedding_provider="openai",
            embedding_model=mock_config["embedding_model"],
        )

        os_makedirs_mock = mocker.patch("os.makedirs")

        database_service._create_base_dir()

        os_makedirs_mock.assert_called_once_with(base_path)
