import pytest
from langchain.schema import Document as LangDocument

from docucite.models.document_model import Document
from docucite.models.embedding_model import OpenAIEmbedding


class DocuciteTestSetup:
    @pytest.fixture
    def mock_pages(self):
        page1 = Document(
            page_content="Hello, this is the first page.",
            metadata={"source": "some_path/file.pdf", "page": 1},
        )
        page2 = Document(
            page_content="This is the second page.",
            metadata={"source": "some_path/file.pdf", "page": 2},
        )
        return [page1, page2]

    @pytest.fixture
    def mock_documents(self):
        page1 = Document(
            page_content="""Very useful text. It also contains a new sentence.

            And, as we can see here, even a separate paragraph! Life is crazy.""",
            metadata={"page": 1, "title": "Greatest book"},
        )
        page2 = Document(
            page_content="""Another day, another sentence.
                            We need them all for testing. Let's go!!!""",
            metadata={"page": 2, "title": "Greatest book"},
        )
        return [page1, page2]

    @pytest.fixture
    def mock_documents_missing_metadata(self):
        page1 = Document(
            page_content="""Very useful text. It also contains a new sentence.

            And, as we can see here, even a separate paragraph! Life is crazy.""",
            metadata={},
        )
        page2 = Document(
            page_content="""Another day, another sentence.
                            We need them all for testing. Let's go!!!""",
            metadata=None,
        )
        return [page1, page2]

    @pytest.fixture
    def mock_documents_metadata_title_missing(self):
        page1 = Document(
            page_content="""Very useful text. It also contains a new sentence.

            And, as we can see here, even a separate paragraph! Life is crazy.""",
            metadata={"page": 1},
        )
        page2 = Document(
            page_content="""Another day, another sentence.
                            We need them all for testing. Let's go!!!""",
            metadata={"page": 2},
        )
        return [page1, page2]

    @pytest.fixture
    def mock_openai_embedding(self):
        class MockOpenAI:
            def __init__(self):
                pass

            class embeddings:
                def create(input, model):
                    return []

        return MockOpenAI

    @pytest.fixture
    def mock_openai_embedding_values(self, mocker):
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
        return embedding

    @pytest.fixture
    def mock_documents_best_book(self):
        page3 = Document(
            page_content="""Hi there, this is the best book.

            We talk about books and text books and all good things book. Oh, did
            I mention book before? Another topic is best, the best. This is
            the best book. Not to be confused with the Greatest Book. This, is
            also available now.""",
            metadata={"page": 1, "title": "Best book"},
        )
        return [page3]

    @pytest.fixture
    def expected_document(self):
        return Document(
            page_content="""Very useful text. It also contains a new sentence.

            And, as we can see here, even a separate paragraph! Life is crazy.""",
            metadata={"page": 1, "title": "Greatest book"},
        )

    @pytest.fixture
    def mock_lang_documents(self):
        page1 = LangDocument(
            page_content="""Very useful text. It also contains a new sentence.

            And, as we can see here, even a separate paragraph! Life is crazy.""",
            metadata={"page": 1, "title": "Greatest book"},
        )
        page2 = LangDocument(
            page_content="""Another day, another sentence.
                            We need them all for testing. Let's go!!!""",
            metadata={"page": 2, "title": "Greatest book"},
        )
        return [page1, page2]

    @pytest.fixture
    def mock_openai_response(self, mocker):
        mock_response = mocker.Mock()
        mocker.patch.object(mock_response, "choices", [mocker.Mock()])
        mocker.patch.object(mock_response.choices[0], "message", mocker.Mock())
        mocker.patch.object(
            mock_response.choices[0].message, "content", "This is the response."
        )
        mock_openai = mocker.Mock()
        mocker.patch.object(
            mock_openai.chat.completions, "create", return_value=mock_response
        )
        return mock_openai

    @pytest.fixture
    def mock_config(self):
        base_path = "path"
        name = ""
        embedding_provider = ""
        embedding_model = ""
        return {
            "path": base_path,
            "name": name,
            "num_search_res": 2,
            "embedding_provider": embedding_provider,
            "embedding_model": embedding_model,
        }
