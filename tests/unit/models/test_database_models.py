import pytest
import chromadb
from docucite.models.database_model import ChromaDatabase

from tests import BaseTest
from tests.unit.services import DocuciteTestSetup


class TestChromaDatabaseModel(BaseTest, DocuciteTestSetup):
    @pytest.fixture
    def mock_chromadb_client(self):
        pass

    @pytest.fixture
    def mock_chroma_db(self, mocker, mock_openai_embedding_values):
        mocker.patch.object(chromadb, "PersistentClient", autospec=True)

        mock_db = ChromaDatabase(
            persist_directory="base",
            num_search_results=2,
            embedding_function=mock_openai_embedding_values,
        )
        return mock_db

    @pytest.mark.skip()
    def test_add_documents(self, mocker, mock_chroma_db, mock_documents):
        mocked_persistent_client_instance = chromadb.PersistentClient.return_value

        res = mock_chroma_db.add_documents(mock_documents)
        assert res == True
        assert mock_chroma_db.collection != None

    def test_delete_documents(self):
        pass

    def test_query(self):
        pass

    def test_get_number_of_documents(self):
        pass

    def test_init_collection(self):
        pass

    def test_get_number_of_documents_by_title(self):
        pass
