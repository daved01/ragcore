from abc import ABC, abstractmethod
from typing import Optional, Any, Mapping, Sized
import uuid
import chromadb

from ragcore.shared.constants import DataConstants, DatabaseConstants
from ragcore.models.embedding_model import BaseEmbedding
from ragcore.models.document_model import Document


NAME_MAIN_COLLECTION = "main_collection"


class BaseVectorDatabaseModel(ABC):
    """Abstract Base Class for vector database models.

    The BaseVectorDatabaseModel defines the interface for vector database models, serving as a base class for
    concrete implementations. Subclasses must implement the abstract methods to provide functionality for adding,
    deleting, querying, and retrieving the number of documents in the database.

    """

    @abstractmethod
    def add_documents(self, documents: list[Document]) -> bool:
        """Adds documents to the database.

        Args:
            documents: A list of documents ``Document`` to be added to the database.

        Returns:
            True if documents have been added, False otherwise.

        """

    @abstractmethod
    def delete_documents(self, title: str) -> bool:
        """Deletes all documents with title `title` from the database.

        Args:
            title: The title of the documents to be deleted.

        Returns:
            True if documents have been delete, False otherwise.

        """

    @abstractmethod
    def query(self, query: str) -> Optional[list[Document]]:
        """Queries the database with a query using a similarity metric.

        Args:
            query: A query as a string.

        Returns:
            A list of documents ``Document``, or None if no documents could be retrieved.

        """

    @abstractmethod
    def get_number_of_documents(self) -> int:
        """Returns the total number of documents in the database."""


class BaseLocalVectorDatabaseModel(BaseVectorDatabaseModel):
    """Base class for local databases.

    Attributes:
        persist_directory: Path to a folder in which the local database should be created.

        embedding_function: Embedding of type ``BaseEmbedding`` to be used to create vector representations of inputs.
    """

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
    """Chroma database.

    Chroma allows to create collections, which are groups of documents. In this class, a single
    collection is used for all documents.

    For more information on Chroma, see: https://www.trychroma.com.

    Attributes:
        persist_directory: Path to a folder in which the local database should be created.

        num_search_results: The number of results to be returned for a query.

        embedding_function: Embedding of type ``BaseEmbedding`` to be used to create vector representations of inputs.

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
        """Adds documents to the Chroma database.

        In the database, each ID must be unique.

        To prevent documents from the same source, say the same PDF file, from being added more than once,
        we check if a document with the same title already exists in the database. Only if it does not can the
        documents be added.

        Args:
            documents: A list of documents.

        Returns:
            True if the document has been added, False otherwise.

        """
        docs = [doc.content for doc in documents]
        metadatas: Any = [data.metadata for data in documents]
        embeddings: Any = self.embedding.embed_texts(docs)
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
        """Deletes all documents with the given title.

        Args:
            title: The title of the documents to be deleted.

        Returns:
            True if documents have been deleted, False otherwise.

        """

        num_docs_before = self._get_number_of_documents_by_title(title)
        self.collection.delete(where={DataConstants.KEY_TITLE: title})
        num_docs_after = self._get_number_of_documents_by_title(title)

        return not num_docs_before == num_docs_after

    def query(self, query: str) -> Optional[list[Document]]:
        """Queries the database with a query.

        To perform the query on the database, vector representations is created from the query first.

        Args:
            query: A query to query the database with.

        Returns:
            A list of results from the database, or None if no results could be retrieved.

        """
        embeddings: Any = self.embedding.embed_texts([query])
        response = self.collection.query(
            query_embeddings=embeddings, n_results=self.num_search_results
        )

        if not response:
            return []

        # Create Documents.
        documents = []

        # We give it only one query, consequently there is only one set of `num_search_results`
        # documents in the response, so why we can index with `0`.
        response_docs_list = response["documents"]
        response_metadata_list = response["metadatas"]

        if not response_docs_list or not response_metadata_list:
            return []

        response_docs = response_docs_list[0]
        response_metadata = response_metadata_list[0]

        for doc, metadata in zip(response_docs, response_metadata):
            metadata_mapping: Mapping[str, Any] = metadata
            documents.append(
                Document(
                    content=doc,
                    title=str(metadata.get("title", "")),
                    metadata=metadata_mapping,
                )
            )

        return documents

    def get_number_of_documents(self) -> int:
        """Returns the number of documents in the collection.

        We use only one collection, so getting all documents in the database is equal to
        getting all documenst in the main collection.

        Returns:
            The number of documents in the database.

        """
        return self.collection.count()

    def _init_collection(self) -> chromadb.Collection:
        """Gets the main collection or creates it."""
        try:
            return self.client.get_collection(name=NAME_MAIN_COLLECTION)
        except ValueError:
            return self.client.create_collection(name=NAME_MAIN_COLLECTION)

    def _get_number_of_documents_by_title(self, title: Optional[str]) -> int:
        """Returns the number of documents with the title `title`.

        If no title is given, returns 0.

        """
        if not title:
            return 0

        metadata = self.collection.get(
            where={DataConstants.KEY_TITLE: title},
            include=["metadatas"],
        ).get(DatabaseConstants.KEY_CHROMA_METADATAS, [])

        if not isinstance(metadata, Sized):
            return 0
        return len(metadata)
