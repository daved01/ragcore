import pytest

from docucite.services.text_splitter_service import TextSplitterService
from tests import BaseTest
from tests.unit.services import DocuciteTestSetup


class TestTextSplitterService(BaseTest, DocuciteTestSetup):
    @pytest.mark.parametrize(
        "split, expected_num_docs",
        [((1000, 200), 2), ((50, 10), 6), ((106, 10), 3), ((10, 4), 28), ((50, 0), 6)],
    )
    def test_split_documents(
        self, split, expected_num_docs, mock_documents, expected_document
    ):
        chunk_size, chunk_overlap = split[0], split[1]
        splitter_service = TextSplitterService(chunk_size, chunk_overlap)
        splits = splitter_service.split_documents(mock_documents)
        assert len(splits) == expected_num_docs

    def test_split_documents_no_docs(self):
        chunk_size, chunk_overlap = 1000, 100
        splitter_service = TextSplitterService(chunk_size, chunk_overlap)
        splits = splitter_service.split_documents([])
        assert len(splits) == 0
