from logging import Logger

from docucite.models.document_model import Document
from docucite.models.prompt_model import PromptGenerator
from docucite.models.llm_model import OpenAIModel, AzureModel
from docucite.errors import LLMError, PromptError, UserConfigurationError


class LLMService:
    def __init__(self, logger: Logger, llm_name: str, llm_temperature=0) -> None:
        self.logger = logger
        self.llm_name = llm_name
        self.llm_temperature = llm_temperature
        self.llm = None

    def initialize_llm(self):
        model_classes = {"openai": OpenAIModel, "azure": AzureModel}

        model_class = model_classes.get(self.llm_name)

        if model_class:
            self.llm = model_class(self.llm_name, self.llm_temperature)
        else:
            raise UserConfigurationError(f"Unsupported model name: {self.llm_name}")
        self.logger.info(
            f"Initialized LLM of type `{self.llm_name}` with temperature {self.llm_temperature}."
        )

    def create_prompt(self, question: str, context: list[Document]) -> str:
        if not question:
            raise PromptError("Tried to create prompt, but no question provided.")
        prompt_template = PromptGenerator()
        context_str = self.document_to_str(context)
        prompt = prompt_template.get_prompt(question, context_str)
        self.logger.info(
            f"Created prompt from question and {len(context)} documents as context."
        )
        return prompt

    def make_llm_request(self, prompt: str) -> str:
        if not self.llm:
            raise LLMError("Tried to make a request, but the llm is not initialized.")

        self.logger.info(f"Sending request to llm of type {self.llm_name} ...")
        response: str = self.llm.predict(text=prompt)
        self.logger.info("Received response from llm.")
        return response

    @staticmethod
    def document_to_str(docs: list[Document]) -> str:
        """Extracts the content from a list of Documents into a line-separated string."""
        docs_text = []
        for _, doc in enumerate(docs):
            docs_text.append(doc.page_content)
        return "\n".join(docs_text)
