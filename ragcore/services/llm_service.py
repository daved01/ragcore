from logging import Logger
from typing import Optional

from ragcore.models.document_model import Document
from ragcore.models.prompt_model import PromptGenerator
from ragcore.models.llm_model import OpenAIModel, AzureOpenAIModel
from ragcore.shared.constants import ConfigurationConstants
from ragcore.shared.errors import LLMError, PromptError, UserConfigurationError
from ragcore.shared.utils import document_to_str
from ragcore.models.config_model import LLMConfiguration


class LLMService:
    """Initializes a Large Language Model and handles requests made to it.

    Currently supported providers are:
        - OpenAI
        - AzureOpenAI

    Attributes:
        logger: A logger instance.
        llm_provider: The provider for the LLM.
        llm_model: The name of the LLM, as specified by the provider.
        llm_config: A configuration for the LLM.

    """

    def __init__(
        self,
        logger: Logger,
        config: LLMConfiguration,
    ) -> None:
        self.logger = logger
        self.llm_provider = config.provider
        self.llm_model = config.model
        self.llm_config = {
            ConfigurationConstants.KEY_AZURE_OPENAI_AZURE_ENDPOINT: config.endpoint,
            ConfigurationConstants.KEY_AZURE_OPENAI_API_VERSION: config.api_version,
        }
        self.llm = None

    def initialize_llm(self):
        """Initializes the selected Large Language Model from the specified provider.

        Make sure to have environment variables set as required by the selected provider.

        Examples:
            - OpenAI: ``OPENAI_API_KEY``
            - AzureOpenAI: ``AZURE_OPENAI_API_KEY``
        """
        model_classes = {
            ConfigurationConstants.LLM_PROVIDER_OPENAI: OpenAIModel,
            ConfigurationConstants.LLM_PROVIDER_AZUREOPENAI: AzureOpenAIModel,
        }

        model_class = model_classes.get(self.llm_provider)

        if model_class:
            self.llm = model_class(self.llm_provider, self.llm_model, self.llm_config)
        else:
            raise UserConfigurationError(
                f"Unsupported model provider: {self.llm_provider}"
            )
        self.logger.info(
            f"Initialized LLM of type `{self.llm_provider}` with model `{self.llm_model}`."
        )

    def create_prompt(self, question: str, contexts: list[Document]) -> str:
        """Creates the prompt which is used to make the request.

        The prompt is created from the prompt template and a concatenation of the document
        chunks as strings.

        Args:
            question: A question as string.

            contexts: List of ``Document``. Typically the grounding information for the question from the database.

        Returns:
            A prompt as a string.

        """
        if not question:
            raise PromptError("Tried to create prompt, but no question provided.")
        prompt_generator = PromptGenerator()
        context_str = document_to_str(contexts)
        prompt = prompt_generator.get_prompt(question, context_str)
        self.logger.info(
            f"Created prompt from question and {len(contexts)} documents as context."
        )
        return prompt

    def make_llm_request(self, prompt: str) -> Optional[str]:
        """Makes a request to the initialized Large Language Model.

        Args:
            prompt: A prompt as a string for the request.

        Returns:
            The response from the LLM as a string or None if no response could be generated.

        """
        if not prompt:
            return None

        if not self.llm:
            raise LLMError("Tried to make a request, but the llm is not initialized.")

        self.logger.info(f"Sending request to llm of type {self.llm_provider} ...")
        response: str = self.llm.request(text=prompt)
        self.logger.info("Received response from llm.")
        return response
