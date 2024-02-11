import pytest

from ragcore.shared import utils
from tests.unit.services import RAGCoreTestSetup


class TestUtils(RAGCoreTestSetup):
    def test_slice_list_with_even_size(self):
        queries = ["query1", "query2", "query3", "query4", "query5", "query6", "query7"]
        result = utils.slice_list(queries, slice_size=2)
        expected = [
            ["query1", "query2"],
            ["query3", "query4"],
            ["query5", "query6"],
            ["query7"],
        ]
        assert result == expected

    def test_slice_list_with_odd_size(self):
        queries = [
            "query1",
            "query2",
            "query3",
            "query4",
            "query5",
            "query6",
            "query7",
            "query8",
        ]
        result = utils.slice_list(queries, slice_size=3)
        expected = [
            ["query1", "query2", "query3"],
            ["query4", "query5", "query6"],
            ["query7", "query8"],
        ]
        assert result == expected

    def test_slice_list_with_empty_list(self):
        queries = []
        result = utils.slice_list(queries, slice_size=2)
        expected = []
        assert result == expected

    def test_slice_list_with_single_element_list(self):
        queries = ["query1"]
        result = utils.slice_list(queries, slice_size=2)
        expected = [["query1"]]
        assert result == expected

    def test_document_to_str(self, mock_documents):
        string = utils.document_to_str(mock_documents)
        assert isinstance(string, str)
        assert mock_documents[0].content in string
        assert mock_documents[1].content in string
        assert "\n" in string

    def test_document_to_str_no_docs(self):
        empty_string = utils.document_to_str([])
        assert empty_string == ""

    def test_remove_file_extension(self):
        cases = [
            ("Should_remove.pdf", "Should_remove"),
            ("should_not_remove.txt", "should_not_remove.txt"),
            ("should_not_remove", "should_not_remove"),
        ]
        for case, expected in cases:
            assert utils.remove_file_extension(case) == expected

    @pytest.mark.parametrize(
        "input, expected",
        [
            ("Hello", "hello"),
            ("", ""),
            ("HeLLo", "hello"),
            ("!@#$%^&*()", "!@#$%^&*()"),
            ("12345", "12345"),
            ("   None   ", "   none   "),
            (None, ""),
        ],
    )
    def test_custom_key_comparator(self, input, expected):
        assert utils.custom_key_comparator(input) == expected
