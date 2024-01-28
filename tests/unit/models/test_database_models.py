import pytest
from ragcore.models.database_model import ChromaDatabase

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
        mocker.patch.object(chromadb_client.collection, "get", return_value=titles)
        res = chromadb_client._get_number_of_documents_by_title("Existing title")
        assert res == 2

    def test_get_number_of_documents_by_title_no_results(self, mocker, chromadb_client):
        res = chromadb_client._get_number_of_documents_by_title(None)
        assert res == 0
