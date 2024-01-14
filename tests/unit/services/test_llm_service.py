import pytest

from docucite.errors import PromptError, LLMError
from docucite.models.llm_model import LLMModel
from docucite.services.llm_service import LLMService
from tests import BaseTest
from tests.unit.services import DocuciteTestSetup


class TestLLMService(BaseTest, DocuciteTestSetup):
    def test_initialize_llm(self, mock_logger, mocker):
        mocker.patch("langchain.chat_models.ChatOpenAI")

        llm_service = LLMService(mock_logger, "openai")
        assert llm_service.llm is None

        llm_service.initialize_llm()
        assert isinstance(llm_service.llm, LLMModel)

    def test_create_prompt(self, mock_logger, mock_documents):
        llm_service = LLMService(mock_logger, "openai")
        question = "What question is that?"
        prompt = llm_service.create_prompt(question, mock_documents)
        assert isinstance(prompt, str)
        assert mock_documents[0].page_content in prompt
        assert mock_documents[1].page_content in prompt
        assert question in prompt

    def test_create_prompt_no_question(self, mock_logger, mock_documents):
        llm_service = LLMService(mock_logger, "openai")
        question = ""
        with pytest.raises(PromptError):
            llm_service.create_prompt(question, mock_documents)

    def test_make_openai_request(self, mock_logger, mocker, mock_openai_response):
        class MockOpenAI:
            def __init__(self):
                pass

            class chat:
                class completions:
                    def create(model, messages):
                        return mock_openai_response

        mocker.patch("docucite.models.llm_model.OpenAI", MockOpenAI)

        llm_service = LLMService(mock_logger, "openai")
        llm_service.initialize_llm()

        response = llm_service.make_llm_request(prompt="This is a full prompt.")
        assert response == "This is the response!"

    def test_make_azureopenai_request(self, mock_logger, mocker):
        class MockAzureChatOpenAI:
            def __init__(
                self,
                openai_api_type,
                deployment_name,
                openai_api_base,
                openai_api_key,
                openai_api_version,
            ):
                pass

            def predict(self, text):
                return "This is the response!"

        mocker.patch("docucite.models.llm_model.AzureChatOpenAI", MockAzureChatOpenAI)

        llm_service = LLMService(mock_logger, "azure")
        llm_service.initialize_llm()

        response = llm_service.make_llm_request(prompt="This is a full prompt.")
        assert response == "This is the response!"

    def test_make_llm_request_no_model_initialized(self, mock_logger):
        llm_service = LLMService(mock_logger, "any")
        with pytest.raises(LLMError):
            llm_service.make_llm_request("")

    def test_document_to_str(self, mock_logger, mock_documents):
        llm_service = LLMService(mock_logger, "any")
        string = llm_service.document_to_str(mock_documents)
        assert isinstance(string, str)
        assert mock_documents[0].page_content in string
        assert mock_documents[1].page_content in string
        assert "\n" in string

    def test_document_to_str_no_docs(self, mock_logger):
        llm_service = LLMService(mock_logger, "any")
        empty_string = llm_service.document_to_str([])
        assert empty_string == ""
