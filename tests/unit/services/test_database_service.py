import pytest

from ragcore.shared.errors import EmbeddingError, DatabaseError, MetadataError
from ragcore.models.database_model import ChromaDatabase
from ragcore.models.embedding_model import BaseEmbedding
from ragcore.services.database_service import DatabaseService

from tests import BaseTest
from tests.unit.services import RAGCoreTestSetup


class TestDatabaseService(BaseTest, RAGCoreTestSetup):
    def test_init_embedding_openai(
        self, mocker, mock_logger, mock_config_localdb, mock_openai_embedding
    ):
        mocker.patch("ragcore.models.embedding_model.OpenAI", mock_openai_embedding)
        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )
        assert isinstance(database_service.embedding.client, mock_openai_embedding)

    def test_init_embedding_invalid_provider(
        self,
        mock_logger,
        mock_config_localdb,
    ):
        with pytest.raises(EmbeddingError):
            mock_config_localdb.embedding_config.provider = "not-supported"
            _ = DatabaseService(
                logger=mock_logger,
                config=mock_config_localdb.database_config,
                embedding_config=mock_config_localdb.embedding_config,
            )

    def test_initialize_local_database(
        self, mocker, mock_logger, mock_config_localdb, mock_openai_embedding
    ):
        mock_database = mocker.Mock()
        mocker.patch("ragcore.models.database_model.ChromaDatabase", mock_database)
        mocker.patch("ragcore.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        database_service.initialize_local_database()

        assert mock_makedirs.call_count == 1
        assert mock_chroma_db_client.call_count == 1
        assert database_service.base_path == "database-base-dir"
        assert database_service.provider == "chroma"
        assert database_service.number_search_results == 2
        assert isinstance(database_service.embedding, BaseEmbedding)

    def test_initialize_local_database_not_supported_database_name(
        self, mocker, mock_logger, mock_config_localdb, mock_openai_embedding
    ):
        mock_database = mocker.Mock()
        mocker.patch("ragcore.models.database_model.ChromaDatabase", mock_database)
        mocker.patch("ragcore.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        mock_config_localdb.database_config.provider = "not-supported"
        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        with pytest.raises(DatabaseError):
            database_service.initialize_local_database()

    def test_add_documents(
        self,
        mocker,
        mock_logger,
        mock_config_localdb,
        mock_openai_embedding,
        mock_documents,
    ):
        mock_add_docs = mocker.Mock()
        mock_database_class = mocker.patch(
            "ragcore.models.database_model.ChromaDatabase"
        )
        mock_database_instance = mock_database_class.return_value
        mock_database_instance.add_documents = mock_add_docs
        mock_database_add_documents = mocker.patch(
            "ragcore.services.database_service.ChromaDatabase.add_documents",
            mock_add_docs,
        )
        mocker.patch("ragcore.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        database_service.initialize_local_database()
        database_service.add_documents(documents=mock_documents)

        assert isinstance(database_service.database, ChromaDatabase)
        assert mock_database_add_documents.call_count == 1

    def test_add_documents_database_not_exist(
        self,
        mocker,
        mock_logger,
        mock_config_localdb,
        mock_openai_embedding,
        mock_documents,
    ):
        mocker.patch("ragcore.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        with pytest.raises(DatabaseError):
            database_service.add_documents(mock_documents)

    def test_add_documents_metadata_title_missing(
        self,
        mocker,
        mock_logger,
        mock_config_localdb,
        mock_openai_embedding,
        mock_documents_metadata_title_missing,
    ):
        mock_database = mocker.Mock()
        mocker.patch("ragcore.models.database_model.ChromaDatabase", mock_database)
        mocker.patch("ragcore.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        database_service.initialize_local_database()
        with pytest.raises(MetadataError):
            database_service.add_documents(mock_documents_metadata_title_missing)

    def test_add_documents_metadata_missing(
        self,
        mocker,
        mock_logger,
        mock_config_localdb,
        mock_openai_embedding,
        mock_documents_missing_metadata,
    ):
        mock_database = mocker.Mock()
        mocker.patch("ragcore.models.database_model.ChromaDatabase", mock_database)
        mocker.patch("ragcore.models.embedding_model.OpenAI", mock_openai_embedding)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        database_service.initialize_local_database()
        with pytest.raises(MetadataError):
            database_service.add_documents(mock_documents_missing_metadata)

    def test_delete_documents(self, mocker, mock_logger, mock_config_localdb):
        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )
        database_service.database = mocker.Mock()
        mock_model = mocker.patch.object(database_service.database, "delete_documents")

        database_service.delete_documents("To delete")

        assert mock_model.call_count == 1

    def test_query(self, mocker, mock_logger, mock_config_localdb, mock_documents):
        mock_database = mocker.Mock()
        mocker.patch("ragcore.models.database_model.ChromaDatabase", mock_database)
        mocker.patch(
            "ragcore.services.database_service.DatabaseService.query",
            return_value="Hello",
        )
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        database_service.initialize_local_database()
        response = database_service.query("my_query")

        assert response == "Hello"

    def test_query_fail(self, mocker, mock_logger, mock_config_localdb):
        mock_database = mocker.Mock()
        mocker.patch("ragcore.models.database_model.ChromaDatabase", mock_database)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        with pytest.raises(DatabaseError):
            database_service.query("my_query")

    @pytest.mark.parametrize("user", [None, "user1"])
    def test_get_titles(self, mocker, mock_logger, mock_config_localdb, user):
        mock_database = mocker.Mock()
        mocker.patch("ragcore.models.database_model.ChromaDatabase", mock_database)
        mocker.patch(
            "ragcore.services.database_service.DatabaseService.get_titles",
            return_value=sorted(["Paper A", "Book A", "book_b"], key=str.lower),
        )
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        database_service.initialize_local_database()
        response = database_service.get_titles(user=user)

        assert response == ["Book A", "book_b", "Paper A"]

    def test_get_titles_no_database(self, mocker, mock_logger, mock_config_localdb):
        mock_database = mocker.Mock()
        mocker.patch("ragcore.models.database_model.ChromaDatabase", mock_database)
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chroma_db_client = mocker.patch("chromadb.PersistentClient")

        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        with pytest.raises(DatabaseError):
            database_service.get_titles()

    def test_create_base_dir(self, mocker, mock_logger, mock_config_localdb):
        mock_config_localdb.database_config.base_path = "/path/to/base"

        database_service = DatabaseService(
            logger=mock_logger,
            config=mock_config_localdb.database_config,
            embedding_config=mock_config_localdb.embedding_config,
        )

        os_makedirs_mock = mocker.patch("os.makedirs")

        database_service._create_base_dir()

        os_makedirs_mock.assert_called_once_with("/path/to/base")
