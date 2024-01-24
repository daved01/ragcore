from docucite.models.embedding_model import OpenAIEmbedding, AzureOpenAIEmbedding
from tests import BaseTest

from tests.unit.services import DocuciteTestSetup


class TestOpenAIEmbeddingModels(BaseTest, DocuciteTestSetup):
    def test_embed_queries(self, mocker):
        mocker.patch("docucite.models.embedding_model.OpenAI", mocker.Mock())
        embedding = OpenAIEmbedding(model="some-model")

        mocker.patch.object(
            embedding.client.embeddings,
            "create",
            return_value=mocker.Mock(
                data=[
                    mocker.Mock(embedding=[0.1, 0.2, 0.3]),
                    mocker.Mock(embedding=[0.6, 0.5, 0.4]),
                ]
            ),
        )

        queries = ["First query", "second query"]
        result = embedding.embed_queries(queries=queries)

        # Assert
        expected_result = [[0.1, 0.2, 0.3], [0.6, 0.5, 0.4]]
        assert result == expected_result


class TestAzureOpenAIEmbeddingModels(BaseTest, DocuciteTestSetup):
    def test_embed_queries(self, mocker):
        mocker.patch("docucite.models.embedding_model.AzureOpenAI", mocker.Mock())
        embedding = AzureOpenAIEmbedding(
            model="some-model", endpoint="https://endpoint.com", api_version="azure-1"
        )

        mocker.patch.object(
            embedding.client.embeddings,
            "create",
            return_value=mocker.Mock(
                data=[
                    mocker.Mock(embedding=[0.1, 0.2, 0.3]),
                    mocker.Mock(embedding=[0.6, 0.5, 0.4]),
                ]
            ),
        )

        queries = ["First query", "second query"]
        result = embedding.embed_queries(queries=queries)

        # Assert
        expected_result = [[0.1, 0.2, 0.3], [0.6, 0.5, 0.4]]
        assert result == expected_result
