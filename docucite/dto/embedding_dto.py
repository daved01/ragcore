from typing import Optional
from langchain.embeddings import OpenAIEmbeddings

from docucite.models.embedding_model import Embedding


# TODO: Tests
class EmbeddingDTO:
    def __init__(self, model: Optional[str]):
        self.model = model

    @classmethod
    def from_docucite(cls, embedding: Embedding):
        return cls(model=embedding.model)

    @classmethod
    def from_langchain(cls, openai_embedding: OpenAIEmbeddings):
        return cls(model=openai_embedding.model)

    def to_docucite(self):
        return Embedding(model=self.model)

    def to_langchain(self):
        return OpenAIEmbeddings(model=self.model)
