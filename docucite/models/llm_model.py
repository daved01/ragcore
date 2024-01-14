from abc import ABC, abstractmethod
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
import os

from docucite.constants import AppConstants


class LLMModel(ABC):
    """Wrapper for llms."""

    def __init__(self, llm_name: str, llm_temperature: int):
        self.llm_name = llm_name
        self.llm_temperature = llm_temperature
        self.llm = self._get_llm()

    @abstractmethod
    def _get_llm(self):
        """Loads the LLM."""

    def predict(self, text: str) -> str:
        """Make a request to an LLM and return the response."""
        return self.llm.predict(text=text)


class OpenAIModel(LLMModel):
    """OpenAI model"""

    def _get_llm(self):
        return ChatOpenAI(
            model_name=AppConstants.OPENAI_LLM_MODEL, temperature=self.llm_temperature
        )


class AzureModel(LLMModel):
    """Azure OpenAI model"""

    def _get_llm(self):
        return AzureChatOpenAI(
            openai_api_type="azure",
            deployment_name=os.getenv("AZURE_DEPLOYMENT_ID"),
            openai_api_base=os.getenv("AZURE_API_BASE_URL"),
            openai_api_key=os.getenv("AZURE_API_KEY"),
            openai_api_version=os.getenv("AZURE_API_VERSION"),
        )
