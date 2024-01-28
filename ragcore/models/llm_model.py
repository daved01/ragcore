from abc import ABC, abstractmethod
import os
from openai import OpenAI, AzureOpenAI
from typing import Optional

from ragcore.shared.constants import ConfigurationConstants, LLMProviderConstants


class LLMModel(ABC):
    """Wrapper for llms."""

    def __init__(
        self,
        llm_provider: str,
        llm_model: str,
        llm_config: Optional[dict[str, str]],
    ):
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.llm_config = llm_config
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
        return OpenAI(api_key=os.getenv(LLMProviderConstants.KEY_OPENAI_API_KEY))

    def predict(self, text: str) -> str:
        response = self.llm.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": text}],
        )
        return response.choices[0].message.content


class AzureOpenAIModel(LLMModel):
    """Azure OpenAI model"""

    def _get_llm(self):
        return AzureOpenAI(
            api_key=os.getenv(LLMProviderConstants.KEY_AZURE_OPENAI_API_KEY),
            api_version=self.llm_config.get(
                ConfigurationConstants.KEY_AZURE_OPENAI_API_VERSION
            ),
            azure_endpoint=self.llm_config.get(
                ConfigurationConstants.KEY_AZURE_OPENAI_AZURE_ENDPOINT
            ),
        )

    def predict(self, text: str) -> str:
        response = self.llm.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": text}],
        )
        return response.choices[0].message.content
