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
            "docucite.constants.AppConstants.KEY_CONFIGURATION_PATH",
            "tests/unit/mock/mock_config.yaml",
        )
        app = DocuCiteApp()

        config = app._get_config(config_file_path="./tests/unit/mock/mock_config.yaml")

        # Database
        assert (
            config[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_DATABASE_NAME
            ]
            == "my_database"
        )
        assert (
            config[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_DOCUMENT_BASE_PATH
            ]
            == "data"
        )
        assert (
            config[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_NUMBER_SEARCH_RESULTS
            ]
            == 5
        )
        # Splitter
        assert (
            config[ConfigurationConstants.KEY_SPLITTER][
                ConfigurationConstants.KEY_CHUNK_SIZE
            ]
            == 1024
        )
        assert (
            config[ConfigurationConstants.KEY_SPLITTER][
                ConfigurationConstants.KEY_CHUNK_OVERLAP
            ]
            == 256
        )
        # Embedding
        assert (
            config[ConfigurationConstants.KEY_EMBEDDING][
                ConfigurationConstants.KEY_EMBEDDING_MODEL
            ]
            == "text-embedding-ada-002"
        )
        # LLM
        assert (
            config[ConfigurationConstants.KEY_LLM][
                ConfigurationConstants.KEY_LLM_PROVIDER
            ]
            == "openai"
        )
        assert (
            config[ConfigurationConstants.KEY_LLM][ConfigurationConstants.KEY_LLM_MODEL]
            == "gpt-3.5-turbo"
        )

    def test_get_config_invalid(self, mocker):
        mocker.patch(
            "docucite.constants.AppConstants.KEY_CONFIGURATION_PATH",
            "tests/unit/mock/mock_config_invalid.yaml",
        )
        app = DocuCiteApp()

        config = app._get_config(
            config_file_path="./tests/unit/mock/mock_config_invalid.yaml"
        )

        key = config[ConfigurationConstants.KEY_DATABASE]
        assert ConfigurationConstants.KEY_DATABASE_BASE_PAH not in key

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
            "docucite.constants.AppConstants.KEY_CONFIGURATION_PATH",
            "tests/unit/mock/mock_config.yaml",
        )
        database_service_mock_load_database = mocker.patch.object(
            DatabaseService, "load_database", side_effect=DatabaseError
        )

        app = DocuCiteApp(config_path="tests/unit/mock/mock_config.yaml")
        app.init_database_service()

        assert app.database_service.database_name == "my_database_1024_256"
        assert app.database_service.base_path == "data/database"
        assert app.database_service.full_path == "data/database/my_database_1024_256"
        assert database_service_mock_load_database.call_count == 1
        assert database_service_mock_create_database.call_count == 1

    def test_init_database_service_load_database(
        self,
        mocker,
        database_service_mock_create_database,
    ):
        mocker.patch(
            "docucite.constants.AppConstants.KEY_CONFIGURATION_PATH",
            "tests/unit/mock/mock_config.yaml",
        )
        database_service_mock_load_database = mocker.patch.object(
            DatabaseService, "load_database", return_value=None
        )

        app = DocuCiteApp(config_path="tests/unit/mock/mock_config.yaml")
        app.init_database_service()

        assert app.database_service.full_path == "data/database/my_database_1024_256"
        assert database_service_mock_load_database.call_count == 1
        assert database_service_mock_create_database.call_count == 0
