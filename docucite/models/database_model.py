from typing import Optional, Any
from langchain_community.vectorstores import Chroma

from docucite.models.embedding_model import Embedding
from docucite.models.document_model import Document
from docucite.dto.document_dto import DocumentDTO
from docucite.dto.embedding_dto import EmbeddingDTO


class VectorDataBaseModel:
    """Wrapper for vector database."""

    def __init__(
        self,
        persist_directory: Optional[str],
        embedding_function: Optional[Embedding],
    ):
        self.chroma = self._init_chroma(
            persist_directory=persist_directory, embedding=embedding_function
        )

    def _init_chroma(
        self, persist_directory: Optional[str], embedding: Optional[Embedding]
    ) -> Chroma:
        embedding_dto = EmbeddingDTO(model=embedding.model if embedding else None)
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_dto.to_langchain(),
        )

    def get(
        self,
        ids: Optional[str] = None,
    ) -> dict[str, Any]:
        return self.chroma.get(ids=ids)

    def add_texts(
        self, texts: list[str], metadatas: Optional[list[dict]] = None
    ) -> list[str]:
        return self.chroma.add_texts(texts=texts, metadatas=metadatas)

    def similarity_search(self, query: str, k: int) -> list[Document]:
        lang_docs = self.chroma.similarity_search(query=query, k=k)

        return DocumentDTO.to_docucite_list(lang_docs)

    @staticmethod
    def from_documents(
        documents: list[Document],
        embedding: Optional[Embedding] = None,
        ids: Optional[list[str]] = None,
        persist_directory: Optional[str] = None,
    ) -> Chroma:
        lang_docs = []
        for document in documents:
            doc_dto = DocumentDTO(
                page_content=document.page_content, metadata=document.metadata
            )
            lang_docs.append(doc_dto.to_langchain())

        embedding_dto = EmbeddingDTO(model=embedding.model if embedding else None)

        chroma_database = Chroma.from_documents(
            documents=lang_docs,
            embedding=embedding_dto.to_langchain(),
            ids=ids,
            persist_directory=persist_directory,
        )

        return chroma_database
