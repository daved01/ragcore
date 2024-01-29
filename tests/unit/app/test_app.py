import pytest

from ragcore.app.app import RAGCore
from ragcore.shared.constants import ConfigurationConstants
from tests import BaseTest


class TestRAGCore(BaseTest):
    @pytest.fixture
    def mock_method_inits(self, mocker):
        mocker.patch("ragcore.app.app.RAGCore._init_database_service", mocker.Mock())
        mocker.patch("ragcore.app.app.RAGCore._init_llm_service", mocker.Mock())

    def test_get_config_verify_config(self, mock_method_inits):
        app = RAGCore(config="./tests/unit/mock/mock_config_no_llms.yaml")

        # Database
        assert (
            app.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_DATABASE_PROVIDER
            ]
            == "chroma"
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_NUMBER_SEARCH_RESULTS
            ]
            == 5
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_DATABASE_BASE_PATH
            ]
            == "data/database"
        )
        # Splitter
        assert (
            app.configuration[ConfigurationConstants.KEY_SPLITTER][
                ConfigurationConstants.KEY_CHUNK_SIZE
            ]
            == 1024
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_SPLITTER][
                ConfigurationConstants.KEY_CHUNK_OVERLAP
            ]
            == 256
        )
        # Embedding
        assert (
            app.configuration[ConfigurationConstants.KEY_EMBEDDING][
                ConfigurationConstants.KEY_EMBEDDING_PROVIDER
            ]
            == "openai"
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_EMBEDDING][
                ConfigurationConstants.KEY_EMBEDDING_MODEL
            ]
            == "text-embedding-ada-002"
        )

    def test_get_config_verify_config_no_path(self, mocker):
        mocker.patch(
            "ragcore.shared.constants.AppConstants.KEY_CONFIGURATION_PATH",
            "tests/unit/mock/mock_config_no_llms.yaml",
        )
        app = RAGCore()

        # Database
        assert (
            app.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_DATABASE_PROVIDER
            ]
            == "chroma"
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_NUMBER_SEARCH_RESULTS
            ]
            == 5
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_DATABASE_BASE_PATH
            ]
            == "data/database"
        )
        # Splitter
        assert (
            app.configuration[ConfigurationConstants.KEY_SPLITTER][
                ConfigurationConstants.KEY_CHUNK_SIZE
            ]
            == 1024
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_SPLITTER][
                ConfigurationConstants.KEY_CHUNK_OVERLAP
            ]
            == 256
        )
        # Embedding
        assert (
            app.configuration[ConfigurationConstants.KEY_EMBEDDING][
                ConfigurationConstants.KEY_EMBEDDING_PROVIDER
            ]
            == "openai"
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_EMBEDDING][
                ConfigurationConstants.KEY_EMBEDDING_MODEL
            ]
            == "text-embedding-ada-002"
        )

    def test_get_config_verify_llm_openai(self, mock_method_inits):
        app = RAGCore(config="./tests/unit/mock/mock_config_openai.yaml")
        assert (
            app.configuration[ConfigurationConstants.KEY_LLM][
                ConfigurationConstants.KEY_LLM_PROVIDER
            ]
            == "openai"
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_LLM][
                ConfigurationConstants.KEY_LLM_MODEL
            ]
            == "gpt-openai"
        )

    def test_get_config_verify_llm_azure(self, mock_method_inits):
        app = RAGCore(config="./tests/unit/mock/mock_config_azure.yaml")
        assert (
            app.configuration[ConfigurationConstants.KEY_LLM][
                ConfigurationConstants.KEY_LLM_PROVIDER
            ]
            == "azure"
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_LLM][
                ConfigurationConstants.KEY_LLM_MODEL
            ]
            == "gpt-azure"
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_LLM][
                ConfigurationConstants.KEY_AZURE_OPENAI_AZURE_ENDPOINT
            ]
            == "https://endpoint.com"
        )
        assert (
            app.configuration[ConfigurationConstants.KEY_LLM][
                ConfigurationConstants.KEY_AZURE_OPENAI_API_VERSION
            ]
            == "some-version"
        )
