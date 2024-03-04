from abc import ABC, abstractmethod
import os
from typing import Optional, Any, Mapping, Sized, Type
import uuid
from requests.exceptions import HTTPError
import chromadb
from pinecone import Pinecone

from ragcore.api.client import PineconeAPIClient
from ragcore.models.embedding_model import BaseEmbedding
from ragcore.models.document_model import Document
from ragcore.shared.constants import DataConstants, DatabaseConstants, APIConstants
from ragcore.shared.errors import DatabaseError
from ragcore.shared.utils import chunk_list


# A default collection to be used when no user is given.
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
        ).get(DatabaseConstants.KEY_METADATAS, [])

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
        try:
            return self.client.get_collection(user)
        except ValueError:
            return self.client.create_collection(user)

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
        ).get(DatabaseConstants.KEY_METADATAS, [])

        if not isinstance(metadata, Sized):
            return 0
        return len(metadata)


class PineconeDatabase(BaseVectorDatabaseModel):
    """Pinecone database.

    To use it, make sure you have your API key under the name ``PINECONE_API_KEY`` available
    as environment variable.

    This implementation uses the Pinecone SDK and the REST API. There is also a gRPC version of the Python client
    with potential for higher upsert speeds, which could be investigated: https://docs.pinecone.io/docs/upsert-data.

    For more information on Pinecone, see: https://www.pinecone.io.

    Attributes:
        base_url: The url pointing to your Pinecone instance.

        num_search_results: The number of results to be returned for a query.

        embedding_function: Embedding of type ``BaseEmbedding`` to be used to create vector representations of inputs.

    """

    def __init__(
        self,
        base_url: str,
        num_search_results: int,
        embedding_function: BaseEmbedding,
    ):
        self.num_search_results: int = num_search_results
        self.embedding: BaseEmbedding = embedding_function
        self.client: Pinecone = Pinecone(
            pool_threads=32
        )  # Requires key PINECONE_API_KEY
        self.index: Type[Pinecone.Index] = self.client.Index(
            DatabaseConstants.KEY_PINECONE_DEFAULT_INDEX, pool_threads=32
        )
        self.api_client = PineconeAPIClient(
            base_url=base_url,
            headers={
                DatabaseConstants.KEY_HEADERS_ACCEPT: "application/json",
                DatabaseConstants.KEY_PINECONE_HEADERS_API_KEY: self._get_api_key(),
            },
        )

    def add_documents(
        self, documents: list[Document], user: Optional[str] = None
    ) -> bool:
        """Adds documents to the database.

        Pinecone is heavily based on IDs while other features are currently missing. For example, it is not possible
        to search the database by metadata without a vector to find titles. That is why we create IDs in the
        format ``<title>#<UID>``. It is possible to filter results by IDs and ID prefixes using the REST API.

        Args:
            documents: A list of documents ``Document`` to be added to the database.

            user: An optional string to identify a user.

        Returns:
            True if documents have been added, False otherwise.

        """
        docs = [doc.content for doc in documents]
        metadatas: Any = [data.metadata for data in documents]
        title = metadatas[0].get(DataConstants.KEY_TITLE)

        # Check if the documents already exist in database.
        if self._get_ids_by_title(
            user=user if user else NAME_MAIN_COLLECTION, title=title
        ):
            return False

        embeddings: Any = self.embedding.embed_texts(docs)

        # Create IDs with the title prefix
        ids = [
            self._title_to_id(title) + "#" + str(uuid.uuid1())
            for _ in range(len(documents))
        ]

        # Construct vectors so they can be inserted. We don't have a field `doc` in Pinecone, so we
        # add this content to metadata as a new field. However, as we don't expect this in metadata
        # in ragcore, we remove `doc` from metadata on retrieval and return a Document as expected.
        vectors = []

        for ind, embedding in enumerate(embeddings):
            metadata = metadatas[ind]
            metadata[DataConstants.KEY_DOC] = docs[ind]
            vectors.append(
                {
                    "id": ids[ind],
                    "values": embedding,
                    "metadata": metadata,
                }
            )

        # Add to database
        chunk_size = 100
        for vector_chunk in chunk_list(vectors, chunk_size):
            try:
                self.index.upsert(
                    namespace=user if user else NAME_MAIN_COLLECTION,
                    vectors=vector_chunk,
                )
            except HTTPError:
                return False
        return True

    def delete_documents(self, title: str, user: Optional[str] = None) -> bool:
        """Deletes all documents with title `title` from the database.

        Args:
            title: The title of the documents to be deleted.

            user: An optional string to identify a user.

        Returns:
            True if documents have been deleted, False otherwise.

        """
        if not title:
            return False
        try:
            ids_to_delete = self._get_ids_by_title(
                user=user if user else NAME_MAIN_COLLECTION, title=title
            )

            if not ids_to_delete:
                return False

            self.index.delete(
                namespace=user if user else NAME_MAIN_COLLECTION, ids=ids_to_delete
            )
        except HTTPError:
            return False
        return True

    def query(self, query: str, user: Optional[str] = None) -> Optional[list[Document]]:
        """Queries the database with the query.

        Args:
            query: A query as a string.

            user: An optional string to identify a user.

        Returns:
            A list of documents ``Document``, or None if no documents could be retrieved.

        """

        embeddings: Any = self.embedding.embed_texts([query])

        response = self.index.query(
            namespace=user if user else NAME_MAIN_COLLECTION,
            top_k=self.num_search_results,
            include_metadata=True,
            vector=embeddings[0],
        )

        if not response:
            return []

        # Create Documents.
        documents = []

        # Extract the parts from matches. Because Pinecone takes one field `metadata`, we have added the
        # document's content to it. In ragcore metadata however, we don't need the `doc` content, so we
        # remove the key-value pair here before we create the Document.
        for match in response.get(DatabaseConstants.KEY_PINECONE_MATCHES):
            metadata = match.get(DatabaseConstants.KEY_METADATA, {})
            doc = metadata.get(DatabaseConstants.KEY_DOC)
            del metadata[
                DatabaseConstants.KEY_DOC
            ]  # We don't have the doc part in ragcore metadata.
            documents.append(
                Document(
                    content=doc,
                    title=str(metadata.get(DatabaseConstants.KEY_TITLE, "")),
                    metadata=metadata,
                )
            )
        return documents

    def get_titles(self, user: Optional[str] = None) -> list[Optional[str]]:
        """Returns the titles owned by the user.

        Currently, this method does not exist in the SDK. Additionally, it is not possible to
        return the metadata along with the vectors from the API endpoint. That is why we
        extract the titles from the IDs.

        Args:
            user: An optional string to identify a user.

        Returns:
            A list of strings with the titles, or an empty list.

        """
        try:
            response = self.api_client.get_paginated(
                endpoint=APIConstants.PINECONE_LIST_VECTORS,
                namespace=user if user else NAME_MAIN_COLLECTION,
            )
        except HTTPError:
            return []

        if not response:
            return []

        # Extract the titles from the IDs in the response
        vectors: Any = response.get(DatabaseConstants.KEY_PINECONE_VECTORS)

        if not vectors:
            return []

        titles = set()

        for vector in vectors:
            curr_id = vector.get(DatabaseConstants.KEY_PINECONE_ID)

            if not curr_id:
                continue

            curr_id_prefix = curr_id.split("#")[0]
            titles.add(self._id_to_title(curr_id_prefix))

        return list(titles)

    def get_number_of_documents(self, user: Optional[str] = None) -> int:
        """Returns the total number of documents in the database.

        Args:
            user: An optional string to identify a user.

        Returns:
            The number of documents owned by the user.

        """
        return len(self.get_titles(user=user if user else NAME_MAIN_COLLECTION))

    def _get_ids_by_title(self, user: str, title: str) -> list[Optional[str]]:
        """Returns a list of IDs given a title."""

        id_prefix = self._title_to_id(
            title
        )  # Part before the hash symbol in the Pinecone ID.

        try:
            response = self.api_client.get_paginated(
                endpoint=APIConstants.PINECONE_LIST_VECTORS,
                namespace=user if user else NAME_MAIN_COLLECTION,
                prefix=id_prefix,
            )

        except HTTPError:
            return []

        if not response:
            return []

        vectors: Any = response.get(DatabaseConstants.KEY_PINECONE_VECTORS)

        if not vectors:
            return []

        ids = set()

        for vector in vectors:
            curr_id = vector.get(DatabaseConstants.KEY_PINECONE_ID)

            # ID from title could be a substring of a retrieved ID.
            if not curr_id or curr_id.split("#")[0] != id_prefix:
                continue

            ids.add(curr_id)

        return list(ids)

    def _get_api_key(self) -> str:
        key = os.getenv(DatabaseConstants.VALUE_PINECONE_API_KEY)
        if not key:
            raise DatabaseError(
                "Could not find API key `PINECONE_API_KEY` in the environment."
            )
        return key

    @staticmethod
    def _title_to_id(title: str) -> str:
        # How long can an ID be? We should probably limit the lenght of an ID.
        return title.replace(" ", "%")

    @staticmethod
    def _id_to_title(title_id: str) -> str:
        return title_id.replace("%", " ")
