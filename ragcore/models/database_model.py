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
    def add_documents(
        self, documents: list[Document], user: Optional[str] = None
    ) -> bool:
        """Adds documents to the database.

        Args:
            documents: A list of documents ``Document`` to be added to the database.

            user: An optional string to identify a user.

        Returns:
            True if documents have been added, False otherwise.

        """

    @abstractmethod
    def delete_documents(self, title: str, user: Optional[str] = None) -> bool:
        """Deletes all documents with title `title` from the database.

        Args:
            title: The title of the documents to be deleted.

            user: An optional string to identify a user.

        Returns:
            True if documents have been delete, False otherwise.

        """

    @abstractmethod
    def query(self, query: str, user: Optional[str] = None) -> Optional[list[Document]]:
        """Queries the database with a query using a similarity metric.

        Args:
            query: A query as a string.

            user: An optional string to identify a user.

        Returns:
            A list of documents ``Document``, or None if no documents could be retrieved.

        """

    @abstractmethod
    def get_titles(self, user: Optional[str] = None) -> list[Optional[str]]:
        """Returns the titles owned by the user.

        Args:
            user: An optional string to identify a user.

        Returns:
            A list of strings with the titles, or an empty list.

        """

    @abstractmethod
    def get_number_of_documents(self, user: Optional[str] = None) -> int:
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

    def add_documents(
        self, documents: list[Document], user: Optional[str] = None
    ) -> bool:
        """Adds documents to the Chroma database.

        In the database, each ID must be unique.

        To prevent documents from the same source, say the same PDF file, from being added more than once,
        we check if a document with the same title already exists in the database. Only if it does not can the
        documents be added.

        Args:
            documents: A list of documents.

            user: An optional string to identify a user.

        Returns:
            True if the document has been added, False otherwise.

        """
        docs = [doc.content for doc in documents]
        metadatas: Any = [data.metadata for data in documents]
        embeddings: Any = self.embedding.embed_texts(docs)
        ids = [str(uuid.uuid1()) for _ in range(len(documents))]

        collection = self._get_collection(user)

        # Check if the documents already exist in database.
        if self._get_number_of_documents_by_title(
            collection, metadatas[0].get(DataConstants.KEY_TITLE)
        ):
            return False

        # Add documents to database.
        collection.add(
            documents=docs,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        return True

    def delete_documents(self, title: str, user: Optional[str] = None) -> bool:
        """Deletes all documents with the given title.

        Args:
            title: The title of the documents to be deleted.

            user: An optional string to identify a user.

        Returns:
            True if documents have been deleted, False otherwise.

        """
        collection = self._get_collection(user)

        num_docs_before = self._get_number_of_documents_by_title(collection, title)
        collection.delete(where={DataConstants.KEY_TITLE: title})
        num_docs_after = self._get_number_of_documents_by_title(collection, title)

        return not num_docs_before == num_docs_after

    def query(self, query: str, user: Optional[str] = None) -> Optional[list[Document]]:
        """Queries the database with a query.

        To perform the query on the database, vector representations is created from the query first.

        Args:
            query: A query to query the database with.

            user: An optional string to identify a user.

        Returns:
            A list of results from the database, or None if no results could be retrieved.

        """
        collection = self._get_collection(user)

        embeddings: Any = self.embedding.embed_texts([query])
        response = collection.query(
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

    def get_titles(self, user: Optional[str] = None) -> list[Optional[str]]:
        """Returns the titles which are owned by the user."""
        collection = self._get_collection(user)

        # Get all metadata items
        metadatas: Any = collection.get(
            include=["metadatas"],
        ).get(DatabaseConstants.KEY_CHROMA_METADATAS, [])

        titles = set()
        for metadata in metadatas:
            title = metadata.get(DataConstants.KEY_TITLE)
            if title:
                titles.add(title)

        return list(titles) if titles else []

    def get_number_of_documents(self, user: Optional[str] = None) -> int:
        """Returns the number of documents in the collection.

        We use only one collection, so getting all documents in the database is equal to
        getting all documenst in the main collection.

        Args:
            user: An optional string to identify a user.

        Returns:
            The number of documents in the database.

        """
        collection = self._get_collection(user)

        return collection.count()

    def _init_collection(self, user: Optional[str] = None) -> chromadb.Collection:
        """Gets the main or the user's collection, or creates one."""
        name = NAME_MAIN_COLLECTION if not user else user

        try:
            return self.client.get_collection(name)
        except ValueError:
            return self.client.create_collection(name)

    def _get_collection(self, user: Optional[str] = None) -> chromadb.Collection:
        """Returns the collection owned by the user, or the default collection.

        If the collection for a user does not exist, a ValueError is raised by the client.

        Args:
            user: An optional string to identify a user.

        Returns:
            A ChromaDB ``Collection``.

        """
        if not user:
            return self.collection
        return self.client.get_collection(user)

    @staticmethod
    def _get_number_of_documents_by_title(
        collection: chromadb.Collection, title: Optional[str]
    ) -> int:
        """Returns the number of documents with the title `title`.

        If no title is given, returns 0.

        """
        if not title:
            return 0

        metadata = collection.get(
            where={DataConstants.KEY_TITLE: title},
            include=["metadatas"],
        ).get(DatabaseConstants.KEY_CHROMA_METADATAS, [])

        if not isinstance(metadata, Sized):
            return 0
        return len(metadata)
