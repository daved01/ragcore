import os
import pytest

from docucite.shared.errors import PromptError, LLMError, UserConfigurationError
from docucite.models.llm_model import LLMModel
from docucite.services.llm_service import LLMService
from tests import BaseTest
from tests.unit.services import DocuciteTestSetup


class TestLLMService(BaseTest, DocuciteTestSetup):
    def test_initialize_llm(self, mock_logger, mocker):
        mocker.patch("langchain.chat_models.ChatOpenAI")

        llm_service = LLMService(mock_logger, "openai", "great-model")
        assert llm_service.llm is None

        llm_service.initialize_llm()
        assert isinstance(llm_service.llm, LLMModel)

    def test_create_prompt(self, mock_logger, mock_documents):
        llm_service = LLMService(mock_logger, "openai", "great-model")
        question = "What question is that?"
        prompt = llm_service.create_prompt(question, mock_documents)
        assert isinstance(prompt, str)
        assert mock_documents[0].page_content in prompt
        assert mock_documents[1].page_content in prompt
        assert question in prompt

    def test_create_prompt_no_question(self, mock_logger, mock_documents):
        llm_service = LLMService(mock_logger, "openai", "great-model")
        question = ""
        with pytest.raises(PromptError):
            llm_service.create_prompt(question, mock_documents)

    def test_init_not_supported_llm(self, mock_logger):
        llm_service = LLMService(mock_logger, "no-supported", "great-model")
        with pytest.raises(UserConfigurationError):
            llm_service.initialize_llm()

    def test_openai_init_request(self, mock_logger, mocker, mock_openai_response):
        mocker.patch(
            "docucite.models.llm_model.OpenAI", return_value=mock_openai_response
        )
        mocker.patch.dict(os.environ, {"OPENAI_API_KEY": "secret-token"})

        llm_service = LLMService(mock_logger, "openai", "great-model")
        llm_service.initialize_llm()

        response = llm_service.make_llm_request(prompt="This is a full prompt.")

        assert response == "This is the response."

    def test_azure_init_request(self, mock_logger, mocker, mock_openai_response):
        mocker.patch(
            "docucite.models.llm_model.AzureOpenAI", return_value=mock_openai_response
        )
        mocker.patch.dict(os.environ, {"AZURE_OPENAI_API_KEY": "secret-token"})

        llm_service = LLMService(
            mock_logger,
            "azure",
            "great-model",
            llm_config={"api_version": "", "endpoint": ""},
        )
        llm_service.initialize_llm()

        response = llm_service.make_llm_request(prompt="This is a full prompt.")
        assert response == "This is the response."

    def test_make_llm_request_no_model_initialized(self, mock_logger):
        llm_service = LLMService(mock_logger, "any", "great-model")
        with pytest.raises(LLMError):
            llm_service.make_llm_request("some prompt")

    def test_make_llm_request_no_prompt(self, mock_logger):
        llm_service = LLMService(mock_logger, "any", "great-model")
        response = llm_service.make_llm_request("")
        assert response is None
