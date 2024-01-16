import pytest
from langchain_community.embeddings import OpenAIEmbeddings

from docucite.models.embedding_model import Embedding
from docucite.dto.embedding_dto import EmbeddingDTO
from tests import BaseTest


class TestEmbeddingDTO(BaseTest):
    def test_to_docucite(self, mocker):
        class MockEmbedding:
            def __init__(self, model="model"):
                self.model = model

        mocker.patch(
            "tests.unit.dto.test_embedding_dto.OpenAIEmbeddings", MockEmbedding
        )
        openai_embedding = OpenAIEmbeddings()
        dto = EmbeddingDTO(model=openai_embedding.model)

        docu_embbedding = dto.to_docucite()

        assert dto.model == "model"
        assert docu_embbedding.model == "model"

    @pytest.mark.parametrize(
        "input_model,expected", [(None, "text-embedding-ada-002"), ("model", "model")]
    )
    def test_to_langchain(self, mocker, input_model, expected):
        class MockEmbedding:
            def __init__(self, model="model"):
                self.model = model

        mocker.patch("docucite.dto.embedding_dto.OpenAIEmbeddings", MockEmbedding)
        if input_model:
            embedding = Embedding(model=input_model)
        else:
            embedding = Embedding()
        dto = EmbeddingDTO(model=embedding.model)

        embedding = dto.to_langchain()

        assert dto.model == expected
        assert embedding.model == expected
