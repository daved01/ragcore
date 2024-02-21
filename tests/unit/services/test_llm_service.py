import os
import pytest

from ragcore.shared.errors import PromptError, LLMError, UserConfigurationError
from ragcore.models.llm_model import BaseLLMModel
from ragcore.services.llm_service import LLMService
from ragcore.models.config_model import LLMConfiguration

from tests import BaseTest
from tests.unit.services import RAGCoreTestSetup


class TestLLMService(BaseTest, RAGCoreTestSetup):
    @pytest.fixture
    def mock_llm_config(self):
        return LLMConfiguration(
            provider="openai", model="great-model", endpoint=None, api_version=None
        )

    def test_initialize_llm(self, mock_logger, mocker, mock_llm_config):
        mocker.patch("langchain.chat_models.ChatOpenAI")

        llm_service = LLMService(mock_logger, mock_llm_config)
        assert llm_service.llm is None

        llm_service.initialize_llm()
        assert isinstance(llm_service.llm, BaseLLMModel)

    def test_create_prompt(self, mock_logger, mock_documents, mock_llm_config):
        llm_service = LLMService(mock_logger, mock_llm_config)
        question = "What question is that?"
        prompt = llm_service.create_prompt(question, mock_documents)
        assert isinstance(prompt, str)
        assert mock_documents[0].content in prompt
        assert mock_documents[1].content in prompt
        assert question in prompt

    def test_create_prompt_no_question(
        self, mock_logger, mock_documents, mock_llm_config
    ):
        llm_service = LLMService(mock_logger, mock_llm_config)
        question = ""
        with pytest.raises(PromptError):
            llm_service.create_prompt(question, mock_documents)

    def test_init_not_supported_llm(self, mock_logger, mock_llm_config):
        mock_llm_config.provider = "not-supported"
        llm_service = LLMService(mock_logger, mock_llm_config)
        with pytest.raises(UserConfigurationError):
            llm_service.initialize_llm()

    def test_openai_init_request(
        self, mock_logger, mocker, mock_openai_response, mock_llm_config
    ):
        mocker.patch(
            "ragcore.models.llm_model.OpenAI", return_value=mock_openai_response
        )
        mocker.patch.dict(os.environ, {"OPENAI_API_KEY": "secret-token"})

        llm_service = LLMService(mock_logger, mock_llm_config)
        llm_service.initialize_llm()

        response = llm_service.make_llm_request(prompt="This is a full prompt.")

        assert response == "This is the response."

    def test_azure_init_request(
        self, mock_logger, mocker, mock_openai_response, mock_llm_config
    ):
        mock_llm_config.provider = "azure"
        mock_llm_config.endpoint = "https://endpoint.com"
        mock_llm_config.api_version = "some-version"
        mocker.patch(
            "ragcore.models.llm_model.AzureOpenAI", return_value=mock_openai_response
        )
        mocker.patch.dict(os.environ, {"AZURE_OPENAI_API_KEY": "secret-token"})

        llm_service = LLMService(
            mock_logger,
            mock_llm_config,
        )
        llm_service.initialize_llm()

        response = llm_service.make_llm_request(prompt="This is a full prompt.")
        assert response == "This is the response."

    def test_make_llm_request_no_model_initialized(self, mock_logger, mock_llm_config):
        llm_service = LLMService(mock_logger, mock_llm_config)
        with pytest.raises(LLMError):
            llm_service.make_llm_request("some prompt")

    def test_make_llm_request_no_prompt(self, mock_logger, mock_llm_config):
        llm_service = LLMService(mock_logger, mock_llm_config)
        response = llm_service.make_llm_request("")
        assert response is None
