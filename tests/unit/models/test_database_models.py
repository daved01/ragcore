import pytest
from requests.exceptions import HTTPError
from ragcore.models.database_model import ChromaDatabase, PineconeDatabase

from tests import BaseTest
from tests.unit.services import RAGCoreTestSetup


class TestChromaDatabaseModel(BaseTest, RAGCoreTestSetup):
    @pytest.fixture
    def chromadb_client(self, mocker, mock_openai_embedding_values):
        mocker.patch("chromadb.PersistentClient")
        mock_db = ChromaDatabase(
            persist_directory="base",
            num_search_results=2,
            embedding_function=mock_openai_embedding_values,
        )
        return mock_db

    def test_add_documents(self, mocker, chromadb_client, mock_documents):
        mocker.patch(
            "ragcore.models.database_model.ChromaDatabase._get_number_of_documents_by_title",
            return_value=0,
        )
        res = chromadb_client.add_documents(mock_documents)
        assert res == True

    def test_add_documents_already_in_database(
        self, mocker, chromadb_client, mock_documents
    ):
        mocker.patch(
            "ragcore.models.database_model.ChromaDatabase._get_number_of_documents_by_title",
            return_value=10,
        )
        res = chromadb_client.add_documents(mock_documents)
        assert res == False

    def test_delete_documents_success(self, mocker, chromadb_client):
        mocker.patch(
            "ragcore.models.database_model.ChromaDatabase._get_number_of_documents_by_title",
            side_effect=[10, 0],
        )
        res = chromadb_client.delete_documents("To be deleted")
        assert res == True

    def test_delete_documents_fail(self, mocker, chromadb_client):
        mocker.patch(
            "ragcore.models.database_model.ChromaDatabase._get_number_of_documents_by_title",
            side_effect=[10, 10],
        )
        res = chromadb_client.delete_documents("To be deleted")
        assert res == False

    def test_query(self, mocker, chromadb_client, mock_documents):
        query_response = {
            "documents": [["Document 1", "Document 2"]],
            "metadatas": [[{"title": "Book 1"}, {"title": "Book 1"}]],
        }
        mocker.patch.object(
            chromadb_client.collection, "query", return_value=query_response
        )
        res = chromadb_client.query("This is the query")

        assert len(res) == 2

    def test_get_number_of_documents(self, mocker, chromadb_client):
        mocker.patch.object(chromadb_client.collection, "count", return_value=42)
        res = chromadb_client.get_number_of_documents()
        assert res == 42

    def test_get_number_of_documents_by_title(self, mocker, chromadb_client):
        titles = {"metadatas": [{"title": "A"}, {"title": "B"}]}

        collection = mocker.Mock()
        mocker.patch.object(collection, "get", return_value=titles)

        res = chromadb_client._get_number_of_documents_by_title(
            collection, "Existing title"
        )
        assert res == 2

    def test_get_number_of_documents_by_title_no_results(self, mocker, chromadb_client):
        collection = mocker.Mock()
        res = chromadb_client._get_number_of_documents_by_title(collection, None)
        assert res == 0


class TestPineconeDatabaseModel:
    @pytest.fixture
    def mock_pinecone_database(self, mocker):
        mocker.patch("ragcore.models.database_model.Pinecone", autospec=True)
        return PineconeDatabase(
            base_url="url", num_search_results=3, embedding_function=mocker.Mock()
        )

    def test_get_ids_by_title_pass(self, mocker, mock_pinecone_database):
        def mock_get_paginated(endpoint, namespace, prefix):
            return {
                "vectors": [
                    {"id": "Existing%Title%A#0102-4312"},
                    {"id": "Existing%Title#0101-4312"},
                    {"id": "Existing%Title%A#1201-3412"},
                    {"id": "Existing%Title#0121-1213"},
                ]
            }

        mocker.patch(
            "ragcore.models.database_model.PineconeAPIClient.get_paginated",
            side_effect=mock_get_paginated,
        )
        # Should find title "Existing Title", but not "Existing Title A"
        returned_ids = mock_pinecone_database._get_ids_by_title(
            user="01", title="Existing Title"
        )
        expected = ["Existing%Title#0101-4312", "Existing%Title#0121-1213"]
        assert len(returned_ids) == len(expected)
        for returned_id in returned_ids:
            assert returned_id in expected

    def test_get_ids_by_title_error(self, mocker, mock_pinecone_database):
        def mock_get_paginated(endpoint, namespace, prefix):
            raise HTTPError("Mocked HTTPError")

        mocker.patch(
            "ragcore.models.database_model.PineconeAPIClient.get_paginated",
            side_effect=mock_get_paginated,
        )

        res = mock_pinecone_database._get_ids_by_title(user="01", title="Missing")
        assert res == []

    @pytest.mark.parametrize(
        "titles, expected",
        [
            ("Title 1", "Title%1"),
            ("Title with Spaces", "Title%with%Spaces"),
            ("", ""),
            (" ", "%"),
            (" Leading spaceNotIgnored ", "%Leading%spaceNotIgnored%"),
        ],
    )
    def test_title_to_id(self, mock_pinecone_database, titles, expected):
        title_id = mock_pinecone_database._title_to_id(titles)
        assert title_id == expected

    @pytest.mark.parametrize(
        "input_id, expected",
        [
            ("Title%1", "Title 1"),
            ("Title%with%Spaces", "Title with Spaces"),
            ("", ""),
            ("%", " "),
            ("%Leading%spaceNotIgnored%", " Leading spaceNotIgnored "),
        ],
    )
    def test_id_to_title(self, mock_pinecone_database, input_id, expected):
        title_id = mock_pinecone_database._id_to_title(input_id)
        assert title_id == expected
