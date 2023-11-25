import pytest

from docucite.app.app import DocuCiteApp
from docucite.constants import ConfigurationConstants
from docucite.errors import UserConfigurationError
from tests import BaseTest


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
        assert config[ConfigurationConstants.KEY_CHUNK_SIZE] == 100
        assert config[ConfigurationConstants.KEY_CHUNK_OVERLAP] == 10

    def test_get_config_string_datatypes(self, mocker):
        mocker.patch(
            "docucite.constants.ConfigurationConstants.CONFIG_FILE_PATH",
            "tests/unit/mock/mock_config_string_datatypes.yaml",
        )
        app = DocuCiteApp()

        config = app._get_config()

        assert config[ConfigurationConstants.KEY_DATABASE_NAME] == "my_database"
        assert config[ConfigurationConstants.KEY_DOCUMENT] == "some_document.txt"
        assert config[ConfigurationConstants.KEY_CHUNK_SIZE] == 100
        assert config[ConfigurationConstants.KEY_CHUNK_OVERLAP] == 10

    def test_get_config_invalid(self, mocker):
        mocker.patch(
            "docucite.constants.ConfigurationConstants.CONFIG_FILE_PATH",
            "tests/unit/mock/mock_config_invalid.yaml",
        )
        app = DocuCiteApp()

        config = app._get_config()

        assert config[ConfigurationConstants.KEY_DATABASE_NAME] == "chroma"
        assert config[ConfigurationConstants.KEY_DOCUMENT] == "my_document.pdf"
        assert config[ConfigurationConstants.KEY_CHUNK_SIZE] == 256
        assert config[ConfigurationConstants.KEY_CHUNK_OVERLAP] == 64

    def test_get_config_missing_document_key(self, mocker):
        mocker.patch(
            "docucite.constants.ConfigurationConstants.CONFIG_FILE_PATH",
            "tests/unit/mock/mock_config_missing_doc_key.yaml",
        )

        with pytest.raises(UserConfigurationError):
            _ = DocuCiteApp()
