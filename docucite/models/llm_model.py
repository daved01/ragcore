from abc import ABC, abstractmethod
from langchain.chat_models import AzureChatOpenAI
import os
from openai import OpenAI

from docucite.constants import AppConstants


class LLMModel(ABC):
    """Wrapper for llms."""

    def __init__(self, llm_provider: str, llm_temperature: int):
        self.llm_provider = llm_provider
        self.llm_temperature = llm_temperature
        self.llm = self._get_llm()

    @abstractmethod
    def _get_llm(self):
        """Initializes the LLM."""

    @abstractmethod
    def predict(self, text: str) -> str:
        """Make a request to an LLM and return the response."""


class OpenAIModel(LLMModel):
    """OpenAI model"""

    def _get_llm(self):
        return OpenAI()

    def predict(self, text: str) -> str:
        response = self.llm.chat.completions.create(
            model=AppConstants.OPENAI_LLM_MODEL,
            messages=[{"role": "user", "content": text}],
        )
        return response.choices[0].message.content


class AzureOpenAIModel(LLMModel):
    """Azure OpenAI model"""

    def _get_llm(self):
        return AzureChatOpenAI(
            openai_api_type="azure",
            deployment_name=os.getenv("AZURE_DEPLOYMENT_ID"),
            openai_api_base=os.getenv("AZURE_API_BASE_URL"),
            openai_api_key=os.getenv("AZURE_API_KEY"),
            openai_api_version=os.getenv("AZURE_API_VERSION"),
        )
