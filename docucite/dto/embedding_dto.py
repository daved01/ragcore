from typing import Optional
from langchain.embeddings import OpenAIEmbeddings

from docucite.models.embedding_model import Embedding


class EmbeddingDTO:
    def __init__(self, model: Optional[str]):
        self.model = model

    def to_docucite(self):
        return Embedding(model=self.model)

    def to_langchain(self):
        return OpenAIEmbeddings(model=self.model)
