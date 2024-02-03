from abc import ABC, abstractmethod
import os
from openai import OpenAI, AzureOpenAI

from ragcore.shared.utils import slice_list
from ragcore.shared.constants import EmbeddingConstants


class BaseEmbedding(ABC):
    """Abstract Base Class for embeddings.

    The BaseEmbedding defines the interface for embedding models, serving as a base class for
    concrete implementations. Subclasses must implement the abstract method to provide functionality for embedding a
    list of strings.

    """

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Creates a list of embedding vectors for a list of text strings.

        Args:
            texts: A list of strings to create embeddings from.

        Returns:
            A list of embedding vectors.

        """


class BaseOpenAIEmbeddings(BaseEmbedding):
    """Base class for OpenAI and AzureOpenAI embeddings.

    A class to implement the embedding method ``embed_texts`` which is the same for
    both OpenAI embedding models and AzureOpenAI models.

    Attributes:
        client: The client for the embedding provider, either OpenAI or AzureOpenAI.

    """

    client: OpenAI | AzureOpenAI
    model: str

    def __init__(self, client: OpenAI | AzureOpenAI) -> None:
        self.client = client

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Create embedding vectors using the selected client.

        Args:
            texts: A list of text strings.

        Returns:
            A list of embedding vectors, one vector for each text element.

        """
        embedding_vectors = []

        query_slices: list[list[str]] = slice_list(texts, 200)

        for query_slice in query_slices:
            response = self.client.embeddings.create(
                input=query_slice, model=self.model
            )
            for i in range(len(query_slice)):
                embedding_vectors.append(response.data[i].embedding)

        return embedding_vectors


class OpenAIEmbedding(BaseOpenAIEmbeddings):
    """Class for OpenAI embedding models.

    Note that you must have your API key for OpenAI ``OPENAI_API_KEY`` set.

    For more information see: https://platform.openai.com/docs/guides/embeddings

    Attributes:
        model: The string for the model which should be used, as specified by OpenAI.

    """

    def __init__(self, model: str):
        self.model = model
        client = OpenAI()  # Openai api key env variable must be set.
        super().__init__(client)


class AzureOpenAIEmbedding(BaseOpenAIEmbeddings):
    """Class for Azure OpenAI embedding models.

    Note that you must have your API key for OpenAI ``AZURE_OPENAI_API_KEY`` set.

    For more information see: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#embeddings-models

    Attributes:
        model: The string for the model which should be used, as specified by Azure OpenAI.

        api_version: The version string of the deployment.

        endpoint: The endpoint of the deployment.

    """

    def __init__(self, model: str, api_version: str, endpoint: str):
        self.model = model
        client = AzureOpenAI(
            api_key=os.getenv(EmbeddingConstants.KEY_AZURE_OPENAI_API_KEY),
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        super().__init__(client)
