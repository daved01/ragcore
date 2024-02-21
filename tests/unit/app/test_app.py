import pytest

from ragcore.app import RAGCore
from tests import BaseTest


class TestRAGCore(BaseTest):
    @pytest.fixture
    def mock_method_inits(self, mocker):
        mocker.patch("ragcore.app.RAGCore._init_database_service", mocker.Mock())
        mocker.patch("ragcore.app.RAGCore._init_llm_service", mocker.Mock())

    def test_get_config_verify_config(self, mock_method_inits):
        app = RAGCore(config="./tests/unit/mock/mock_config_no_llms.yaml")

        # Database
        assert app.configuration.database_config.provider == "chroma"
        assert app.configuration.database_config.number_search_results == 5
        assert app.configuration.database_config.base_path == "data/database"
        # Splitter
        assert app.configuration.splitter_config.chunk_size == 1024
        assert app.configuration.splitter_config.chunk_overlap == 256
        # Embedding
        assert app.configuration.embedding_config.provider == "openai"
        assert app.configuration.embedding_config.model == "text-embedding-ada-002"

    def test_get_config_verify_config_no_path(self, mocker):
        mocker.patch(
            "ragcore.shared.constants.AppConstants.KEY_CONFIGURATION_PATH",
            "tests/unit/mock/mock_config_no_llms.yaml",
        )
        app = RAGCore()

        # Database
        assert app.configuration.database_config.provider == "chroma"
        assert app.configuration.database_config.number_search_results == 5
        assert app.configuration.database_config.base_path == "data/database"
        # Splitter
        assert app.configuration.splitter_config.chunk_size == 1024
        assert app.configuration.splitter_config.chunk_overlap == 256
        # Embedding
        assert app.configuration.embedding_config.provider == "openai"
        assert app.configuration.embedding_config.model == "text-embedding-ada-002"

    def test_get_config_verify_llm_openai(self, mock_method_inits):
        app = RAGCore(config="./tests/unit/mock/mock_config_openai.yaml")
        assert app.configuration.llm_config.provider == "openai"
        assert app.configuration.llm_config.model == "gpt-openai"

    def test_get_config_verify_llm_azure(self, mock_method_inits):
        app = RAGCore(config="./tests/unit/mock/mock_config_azure.yaml")
        assert app.configuration.llm_config.provider == "azure"
        assert app.configuration.llm_config.model == "gpt-azure"
        assert app.configuration.llm_config.endpoint == "https://endpoint.com"
        assert app.configuration.llm_config.api_version == "some-version"
