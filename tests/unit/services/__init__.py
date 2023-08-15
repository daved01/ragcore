import pytest

from langchain.schema.document import Document


class DocuciteTestSetup:
    @pytest.fixture
    def mock_documents(self):
        page1 = Document(
            page_content="""Very useful text. It also contains a new sentence.

            And, as we can see here, even a separate paragraph! Life is crazy.""",
            metadata={"page": 1, "title": "Greatest book"},
        )
        page2 = Document(
            page_content="""Another day, another sentence. We need them all for testing. Let's go!!!""",
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
