from openai import OpenAI

from docucite.models.llm_model import OpenAIModel


class TestLLMModel:
    def test_get_llm_chatopenai(self, mocker):
        mocker.patch("langchain.chat_models.ChatOpenAI")
        llm = OpenAIModel(llm_provider="cool_model", llm_temperature=0)
        llm._get_llm()
        assert isinstance(llm.llm, OpenAI)
