from abc import ABC, abstractmethod
import os
from typing import Optional
from openai import OpenAI, AzureOpenAI

from ragcore.shared.constants import ConfigurationConstants, LLMProviderConstants


class BaseLLMModel(ABC):
    """Abstract Base Class for Large Language Model models.

    The BaseLLMModel defines the interface for LLM models, serving as a base class for
    concrete implementations. Subclasses must implement the abstract method to provide functionality for
    generating responses for a given text input.


    Attributes:
        llm_provider: The provider of the LLM model.

        llm_model: The llm from the provder as a string, as specified by the provider.

        llm_config: Configuration for the LLM.

    """

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
    def request(self, text: str) -> str:
        """Perform a request to an LLM and return the response.

        Args:
            text: A string with the request for the LLM.

        Returns:
            A response from the llm as a string.

        """


class OpenAIModel(BaseLLMModel):
    """Class to interact with OpenAI LLMs.

    Make sure to have your API key set in the environment as ``OPENAI_API_KEY``.

    For more information, see: https://platform.openai.com/docs/guides/text-generation

    """

    def _get_llm(self):
        return OpenAI(api_key=os.getenv(LLMProviderConstants.KEY_OPENAI_API_KEY))

    def request(self, text: str) -> str:
        """Perform a request with an OpenAI LLM.

        Args:
            text: The text string for the request.

        Returns:
            The response string from the LLM.

        """
        response = self.llm.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": text}],
        )
        return response.choices[0].message.content


class AzureOpenAIModel(BaseLLMModel):
    """Class to interact with Azure OpenAI LLMs.

    Make sure to have your API key set in the environment as ``AZURE_OPENAI_API_KEY``.

    For more information, see: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models

    """

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

    def request(self, text: str) -> str:
        """Perform a request with an Azure OpenAI LLM.

        Args:
            text: The text string for the request.

        Returns:
            The response string from the LLM.

        """
        response = self.llm.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": text}],
        )
        return response.choices[0].message.content
