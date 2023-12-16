import pytest

from docucite.app.app import DocuCiteApp
from docucite.constants import ConfigurationConstants
from docucite.errors import DatabaseError, UserConfigurationError
from tests import BaseTest
from docucite.services.database_service import DatabaseService
from docucite.models.embedding_model import Embedding


class TestDocuCiteApp(BaseTest):
    def test_get_config_verify_config(self, mocker):
        mocker.patch(
            "docucite.constants.ConfigurationConstants.CONFIG_FILE_PATH",
            "tests/unit/mock/mock_config.yaml",
        )
        app = DocuCiteApp()

        config = app._get_config()

        assert config[ConfigurationConstants.KEY_DATABASE_NAME] == "my_database"
        assert config[ConfigurationConstants.KEY_DOCUMENT] == "some_document.txt"
        assert config[ConfigurationConstants.KEY_CHUNK_SIZE] == 256
        assert config[ConfigurationConstants.KEY_CHUNK_OVERLAP] == 64

    def test_get_config_string_datatypes(self, mocker):
        mocker.patch(
            "docucite.constants.ConfigurationConstants.CONFIG_FILE_PATH",
            "tests/unit/mock/mock_config_string_datatypes.yaml",
        )
        app = DocuCiteApp()

        config = app._get_config()

        assert config[ConfigurationConstants.KEY_DATABASE_NAME] == "my_database"
        assert config[ConfigurationConstants.KEY_DOCUMENT] == "some_document.txt"
        assert config[ConfigurationConstants.KEY_CHUNK_SIZE] == 256
        assert config[ConfigurationConstants.KEY_CHUNK_OVERLAP] == 64

    def test_get_config_invalid(self, mocker):
        mocker.patch(
            "docucite.constants.ConfigurationConstants.CONFIG_FILE_PATH",
            "tests/unit/mock/mock_config_invalid.yaml",
        )
        app = DocuCiteApp()

        config = app._get_config()

        assert config[ConfigurationConstants.KEY_DATABASE_NAME] == "chroma"  # Default
        assert config[ConfigurationConstants.KEY_DOCUMENT] == "my_document.pdf"
        assert config[ConfigurationConstants.KEY_CHUNK_SIZE] == 1024  # Default
        assert config[ConfigurationConstants.KEY_CHUNK_OVERLAP] == 256  # Default

    def test_get_config_missing_document_key(self, mocker):
        mocker.patch(
            "docucite.constants.ConfigurationConstants.CONFIG_FILE_PATH",
            "tests/unit/mock/mock_config_missing_doc_key.yaml",
        )

        with pytest.raises(UserConfigurationError):
            _ = DocuCiteApp()

    @pytest.fixture
    def database_service_mock_create_database(self, mocker):
        return mocker.patch.object(
            DatabaseService, "create_database", return_value=None
        )

    @pytest.fixture
    def mock_openai_embedding(self, mocker):
        return mocker.patch.object(Embedding, "__init__", return_value=None)

    def test_init_database_service_create_database(
        self, mocker, database_service_mock_create_database
    ):
        mocker.patch(
            "docucite.constants.ConfigurationConstants.CONFIG_FILE_PATH",
            "tests/unit/mock/mock_config.yaml",
        )
        database_service_mock_load_database = mocker.patch.object(
            DatabaseService, "load_database", side_effect=DatabaseError
        )

        app = DocuCiteApp()
        app.init_database_service()

        assert app.database_service.database_path == "data/database/my_database_256_64"
        assert database_service_mock_load_database.call_count == 1
        assert database_service_mock_create_database.call_count == 1

    def test_init_database_service_load_database(
        self,
        mocker,
        database_service_mock_create_database,
    ):
        mocker.patch(
            "docucite.constants.ConfigurationConstants.CONFIG_FILE_PATH",
            "tests/unit/mock/mock_config.yaml",
        )
        database_service_mock_load_database = mocker.patch.object(
            DatabaseService, "load_database", return_value=None
        )

        app = DocuCiteApp()
        app.init_database_service()

        assert app.database_service.database_path == "data/database/my_database_256_64"
        assert database_service_mock_load_database.call_count == 1
        assert database_service_mock_create_database.call_count == 0
