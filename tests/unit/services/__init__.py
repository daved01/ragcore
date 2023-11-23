import pytest
from langchain.schema import Document as LangDocument

from docucite.models.document_model import Document


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
    def mock_three_texts(self):
        return ["A", "B", "C"]

    @pytest.fixture
    def mock_three_metadatas(self):
        return [
            {"page": 1, "title": "Best book"},
            {"page": 2, "title": "Best book"},
            {"page": 2, "title": "Best book"},
        ]

    @pytest.fixture
    def mock_two_metadatas(self):
        return [{"page": 1, "title": "Best book"}, {"page": 2, "title": "Best book"}]

    @pytest.fixture
    def mock_two_metadatas_two(self):
        return [{"page": 1, "title": "Good Book"}, {"page": 2, "title": "Good Book"}]

    @pytest.fixture
    def mock_three_metadatas_one_missing_title(self):
        return [
            {"page": 1, "title": "Best book"},
            {"page": 2, "title": "Best book"},
            {"page": 2},
        ]
