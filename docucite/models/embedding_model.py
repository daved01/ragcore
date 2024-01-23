from abc import ABC, abstractmethod
from openai import OpenAI

from docucite.shared.utils import slice_list


class BaseEmbedding(ABC):
    """ABC for embeddings."""

    @abstractmethod
    def embed_queries(self, queries: list[str]) -> list[list[float]]:
        """Creates a list of embeddings for a list of queries."""


class OpenAIEmbedding(BaseEmbedding):
    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI()  # Openai api key env variable must be set.

    def embed_queries(self, queries: list[str]) -> list[list[float]]:
        embedding_vectors = []

        query_slices: list[list[str]] = slice_list(queries, 200)

        for query_slice in query_slices:
            response = self.client.embeddings.create(
                input=query_slice, model=self.model
            )
            for i in range(len(query_slice)):
                embedding_vectors.append(response.data[i].embedding)

        return embedding_vectors
