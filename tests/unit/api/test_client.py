import pytest
from requests import HTTPError

from ragcore.api.client import APIClient, PineconeAPIClient


class BaseAPITests:
    @pytest.fixture
    def mock_api_client(self, mocker):
        mocker.patch("requests.Session", return_value=mocker.Mock())
        return APIClient("https://api-url.com")


class TestAPIClient(BaseAPITests):
    def test_get_success(self, mocker, mock_api_client):
        mocker.patch.object(mock_api_client.session, "get")
        mock_api_client.session.get.return_value.status_code = 200
        mock_api_client.session.get.return_value.json = lambda: {"data": "test"}

        result = mock_api_client.get("/some/endpoint")

        assert result == {"data": "test"}
        mock_api_client.session.get.assert_called_once_with(
            "https://api-url.com/some/endpoint", params={}
        )

    def test_get_with_params(self, mocker, mock_api_client):
        mocker.patch.object(mock_api_client.session, "get")
        mock_api_client.session.get.return_value.status_code = 200
        mock_api_client.session.get.return_value.json = lambda: {"data": "test"}

        result = mock_api_client.get("/endpoint", params={"limit": 10})

        assert result == {"data": "test"}
        mock_api_client.session.get.assert_called_once_with(
            "https://api-url.com/endpoint", params={"limit": 10}
        )

    def test_get_error(self, mocker, mock_api_client):
        mocker.patch.object(mock_api_client.session, "get")
        mock_api_client.session.get.return_value.status_code = 404
        mock_api_client.session.get.return_value.raise_for_status.side_effect = (
            HTTPError()
        )

        with pytest.raises(HTTPError):
            _ = mock_api_client.get("/not/found")

    def test_post_success(self, mocker, mock_api_client):
        mocker.patch.object(mock_api_client.session, "post")
        mock_api_client.session.post.return_value.status_code = 201
        mock_api_client.session.post.return_value.json = lambda: {"message": "created"}

        result = mock_api_client.post("/items", json={"name": "test item"})

        assert result == {"message": "created"}
        mock_api_client.session.post.assert_called_once_with(
            "https://api-url.com/items", data=None, json={"name": "test item"}
        )

    def test_post_with_data(self, mocker, mock_api_client):
        mocker.patch.object(mock_api_client.session, "post")
        mock_api_client.session.post.return_value.status_code = 201
        mock_api_client.session.post.return_value.json = lambda: {"message": "created"}

        result = mock_api_client.post("/items", data={"name": "test item"})

        assert result == {"message": "created"}
        mock_api_client.session.post.assert_called_once_with(
            "https://api-url.com/items", data={"name": "test item"}, json=None
        )

    def test_post_error(self, mocker, mock_api_client):
        mocker.patch.object(mock_api_client.session, "post")
        mock_api_client.session.post.return_value.status_code = 401
        mock_api_client.session.post.return_value.raise_for_status.side_effect = (
            HTTPError()
        )
        mock_api_client.session.post.return_value.json = lambda: {"message": "created"}

        with pytest.raises(HTTPError):
            result = mock_api_client.post("/items", json={"name": "test item"})

    @pytest.mark.parametrize(
        "base_url, endpoint, expected",
        [
            ("https://api-url.com", "users", "https://api-url.com/users"),
            ("https://api-url.com/", "/users", "https://api-url.com/users"),
            ("https://api-url.com/", "users/", "https://api-url.com/users/"),
            ("http://localhost:8000/", "items/1", "http://localhost:8000/items/1"),
        ],
    )
    def test_build_url_parametrized(self, base_url, endpoint, expected):
        api_client = APIClient(base_url=base_url)
        result = api_client._build_url(endpoint)
        assert result == expected


class TestPineconeAPIClient(BaseAPITests):
    @pytest.fixture
    def mock_pinecone_api_client(self, mocker):
        mocker.patch("requests.Session", return_value=mocker.Mock())
        mock_api_client = PineconeAPIClient("https://api-url.com")
        mocker.patch.object(mock_api_client.session, "get")
        return mock_api_client

    def test_get_paginated_one_page(self, mocker, mock_pinecone_api_client):
        def mock_response():
            response_mock = mocker.Mock()
            response_mock.status_code = 200
            response_mock.json.return_value = {
                "vectors": [{"id": "1"}, {"id": "2"}],
                "namespace": "example",
            }
            return response_mock

        mock_pinecone_api_client.session.get.return_value = mock_response()

        result = mock_pinecone_api_client.get_paginated("/data", "example")

        assert result == {
            "vectors": [{"id": "1"}, {"id": "2"}],
            "namespace": "example",
        }

    def test_get_paginated_success(self, mocker, mock_pinecone_api_client):
        def mock_response(status_code, json_data):
            response_mock = mocker.Mock()
            response_mock.status_code = status_code
            response_mock.json.return_value = json_data
            return response_mock

        mock_pinecone_api_client.session.get.side_effect = [
            mock_response(
                200,
                {
                    "vectors": [{"id": "1"}, {"id": "2"}],
                    "namespace": "example",
                    "pagination": {"next": "some-token"},
                },
            ),
            mock_response(
                200,
                {
                    "vectors": [{"id": "3"}],
                    "namespace": "example",
                },
            ),
        ]

        result = mock_pinecone_api_client.get_paginated("/data", "example")

        assert result == {
            "vectors": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
            "namespace": "example",
        }
