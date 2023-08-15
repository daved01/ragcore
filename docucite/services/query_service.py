"""
Core business layer
Contains:
- Document uploading
- Loading the database
- Construct a prompt from the question and the template
- Process the answer
-
"""
from logging import Logger
from langchain.embeddings.openai import OpenAIEmbeddings


class QueryService:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def load_embeddings(self) -> None:
        """Load embeddings from database"""
        embedding = OpenAIEmbeddings()  # type: ignore
        self.vectordb = Chroma(
            persist_directory=self.persist_directory, embedding_function=embedding
        )
        self.logger.info(f"Loaded embeddings from path: {self.persist_directory}.")

    def create_prompt(self, question: str, context: str) -> str:
        pass

    def make_llm_request(self, prompt: str) -> None:
        pass
