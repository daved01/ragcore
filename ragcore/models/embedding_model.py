from abc import ABC, abstractmethod
from openai import OpenAI, AzureOpenAI
import os

from ragcore.shared.utils import slice_list
from ragcore.shared.constants import EmbeddingConstants


class BaseEmbedding(ABC):
    """ABC for embeddings."""

    @abstractmethod
    def embed_queries(self, queries: list[str]) -> list[list[float]]:
        """Creates a list of embeddings for a list of queries."""


class BaseOpenAIEmbeddings(BaseEmbedding):
    """Class for OpenAI and AzureOpenAI embeddings."""

    client: OpenAI | AzureOpenAI
    model: str

    def __init__(self, client: OpenAI | AzureOpenAI) -> None:
        self.client = client

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


class OpenAIEmbedding(BaseOpenAIEmbeddings):
    def __init__(self, model: str):
        self.model = model
        client = OpenAI()  # Openai api key env variable must be set.
        super().__init__(client)


class AzureOpenAIEmbedding(BaseOpenAIEmbeddings):
    def __init__(self, model: str, api_version: str, endpoint: str):
        self.model = model
        client = AzureOpenAI(
            api_key=os.getenv(EmbeddingConstants.KEY_AZURE_OPENAI_API_KEY),
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        super().__init__(client)
