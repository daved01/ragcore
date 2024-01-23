from docucite.shared import utils


def test_slice_list_with_even_size():
    queries = ["query1", "query2", "query3", "query4", "query5", "query6", "query7"]
    result = utils.slice_list(queries, slice_size=2)
    expected = [
        ["query1", "query2"],
        ["query3", "query4"],
        ["query5", "query6"],
        ["query7"],
    ]
    assert result == expected


def test_slice_list_with_odd_size():
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


def test_slice_list_with_empty_list():
    queries = []
    result = utils.slice_list(queries, slice_size=2)
    expected = []
    assert result == expected


def test_slice_list_with_single_element_list():
    queries = ["query1"]
    result = utils.slice_list(queries, slice_size=2)
    expected = [["query1"]]
    assert result == expected
