from langchain.chat_models import ChatOpenAI


class LLMModel:
    """Wrapper for llms."""

    def __init__(self, llm_name: str, llm_temperature: int):
        self.llm_name = llm_name
        self.llm_temperature = llm_temperature
        self.llm = self._get_llm()

    def _get_llm(self):
        return ChatOpenAI(model_name=self.llm_name, temperature=self.llm_temperature)

    def predict(self, text: str) -> str:
        """Make a request to an LLM and return the response."""
        return self.llm.predict(text=text)
