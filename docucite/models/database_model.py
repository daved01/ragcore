from typing import Optional, Protocol, Any

from langchain.vectorstores import Chroma

from docucite.models.embedding_model import Embedding
from docucite.constants import AppConstants
from docucite.models.document_model import Document


class ChromaProtocol(Protocol):
    def get(self, ids: Optional[str]) -> dict[str, Any]:
        ...


class VectorDataBaseModel:
    """Wrapper for vector database."""

    def __init__(
        self, persist_directory: Optional[str], embedding_function: Optional[Embedding]
    ):
        self.persist_directory = persist_directory
        self.embeddings = embedding_function
        self.chroma = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )

    def get(
        self,
        ids: Optional[str] = None,
    ) -> dict[str, Any]:
        return self.chroma.get(ids=ids)

    def add_texts(
        self, texts: str, metadatas: Optional[list[dict]] = None
    ) -> list[str]:
        return self.chroma.add_texts(texts=texts, metadatas=metadatas)

    @staticmethod
    def from_documents(
        documents: list[Document],
        embedding: Optional[Embedding] = None,
        ids: Optional[list[str]] = None,
        persist_directory: Optional[str] = None,
    ) -> Chroma:
        return Chroma.from_documents(
            documents=documents,
            embedding=embedding,
            ids=ids,
            persist_directory=persist_directory,
        )

    def similarity_search(
        self, query: str, k: int = AppConstants.DATABASE_SEARCH_DEFAULT_K
    ) -> list[Document]:
        return self.chroma.similarity_search(query=query, k=k)
