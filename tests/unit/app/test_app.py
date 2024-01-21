import pytest

from docucite.app.app import DocuCiteApp
from docucite.constants import ConfigurationConstants
from docucite.errors import DatabaseError
from tests import BaseTest
from docucite.services.database_service import DatabaseService
from docucite.models.embedding_model import OpenAIEmbedding


class TestDocuCiteApp(BaseTest):
    def test_get_config_verify_config(self):
        app = DocuCiteApp(config_path="./tests/unit/mock/mock_config_no_llms.yaml")

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
        assert (
            app.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_DOCUMENT_BASE_PATH
            ]
            == "data"
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
            "docucite.constants.AppConstants.KEY_CONFIGURATION_PATH",
            "tests/unit/mock/mock_config_no_llms.yaml",
        )
        app = DocuCiteApp()

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
        assert (
            app.configuration[ConfigurationConstants.KEY_DATABASE][
                ConfigurationConstants.KEY_DOCUMENT_BASE_PATH
            ]
            == "data"
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

    def test_get_config_verify_llm_openai(self):
        app = DocuCiteApp(config_path="./tests/unit/mock/mock_config_openai.yaml")
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

    def test_get_config_verify_llm_azure(self):
        app = DocuCiteApp(config_path="./tests/unit/mock/mock_config_azure.yaml")
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
