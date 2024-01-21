from abc import ABC, abstractmethod
import chromadb
from typing import Optional, Any
import uuid

from docucite.constants import DataConstants, DatabaseConstants
from docucite.models.embedding_model import BaseEmbedding
from docucite.models.document_model import Document


class BaseVectorDatabaseModel(ABC):
    """
    ABC for vector database.
    Collections - Groups of documents.
    Documents - Hold the data.
    """

    @abstractmethod
    def add_documents(self, documents: list[Document]) -> bool:
        """
        Adds documents to the database. Returns True if
        documents have been added, otherwise False.
        """

    @abstractmethod
    def delete_documents(self, title: str) -> bool:
        """Deletes all documents with title `title` from the database."""

    @abstractmethod
    def query(self, query: str) -> list[Document]:
        """Queries the database with a query using a similarity metric."""

    @abstractmethod
    def get_number_of_documents(self) -> int:
        """Returns the number of documents in the database"""


class BaseLocalVectorDatabaseModel(BaseVectorDatabaseModel):
    """Base class for local databases."""

    def __init__(
        self,
        persist_directory: Optional[str],
        embedding_function: BaseEmbedding,
    ):
        pass


class BaseRemoteVectorDatabaseModel(BaseVectorDatabaseModel):
    """Base class for remote databases."""

    def __init__(self):
        pass


class ChromaDatabase(BaseLocalVectorDatabaseModel):
    """
    We use a single collection for all documents.
    """

    def __init__(
        self,
        persist_directory: str,
        num_search_results: int,
        embedding_function: BaseEmbedding,
    ):
        self.persist_directory: str = persist_directory
        self.num_search_results: int = num_search_results
        self.embedding: BaseEmbedding = embedding_function
        self.client: chromadb.ClientAPI = chromadb.PersistentClient(
            path=self.persist_directory
        )
        self.collection: chromadb.Collection = self._init_collection()

    def add_documents(self, documents: list[Document]) -> bool:
        """
        Adds documents to the database. Each ID is unique in the database.
        Since we generate IDs here, we enforce uniqueness with
        the document title in the metadata.
        Returns True if the documents have been added, otherwise False.
        """
        docs = [doc.page_content for doc in documents]
        metadatas = [data.metadata for data in documents]
        embeddings = self.embedding.embed_queries(docs)
        ids = [str(uuid.uuid1()) for _ in range(len(documents))]

        # Check if the documents already exist in database.
        if self._get_number_of_documents_by_title(
            metadatas[0].get(DataConstants.KEY_TITLE)
        ):
            return False

        # Add documents to database.
        self.collection.add(
            documents=docs,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        return True

    def delete_documents(self, title: str) -> bool:
        """
        Deletes all documents with the given title.
        """

        num_docs_before = self._get_number_of_documents_by_title(title)
        self.collection.delete(where={DataConstants.KEY_TITLE: title})
        num_docs_after = self._get_number_of_documents_by_title(title)

        return not (num_docs_before == num_docs_after)

    # TODO: Investigate similarity measures
    def query(self, query: str) -> list[Document]:
        embeddings = self.embedding.embed_queries([query])
        response = self.collection.query(
            query_embeddings=embeddings, n_results=self.num_search_results
        )

        # Create Documents.
        documents = []
        response_docs = response[DatabaseConstants.KEY_CHROMA_DOCUMENTS][0]
        response_metadata = response[DatabaseConstants.KEY_CHROMA_METADATAS][0]

        for doc, metadata in zip(response_docs, response_metadata):
            documents.append(Document(page_content=doc, metadata=metadata))

        return documents

    def get_number_of_documents(self) -> int:
        """
        Returns the number of documents in the collection.
        """
        return self.collection.count()

    def _init_collection(self):
        """
        Gets the main collection or creates it.
        """
        NAME_MAIN_COLLECTION = "main_collection"
        try:
            return self.client.get_collection(name=NAME_MAIN_COLLECTION)
        except ValueError:
            return self.client.create_collection(name=NAME_MAIN_COLLECTION)

    def _get_number_of_documents_by_title(self, title: Optional[str]) -> int:
        """
        Returns the number of documents with the title `title`.
        If not title is given, returns 0.
        """
        if not title:
            return 0
        return self.collection.get(
            where={DataConstants.KEY_TITLE: title},
            include=[DatabaseConstants.KEY_CHROMA_METADATAS],
        ).get(DatabaseConstants.KEY_CHROMA_METADATAS)
