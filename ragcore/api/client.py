import re
from typing import Optional
import requests

from ragcore.shared.constants import DatabaseConstants

BASE_URL_PATTERN = re.compile(r"/+$")
ENDPOINT_URL_PATTERN = re.compile(r"^/+")


class APIClient:
    """API client for synchronous API requests.

    Attributes:
        base_url: The base URL for your requests.

        headers: A dict with key-value pairs for the header.
    """

    def __init__(self, base_url: str, headers: Optional[dict[str, str]] = None):
        self.base_url = base_url
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def get(
        self, endpoint: str, params: Optional[dict[str, str]] = None
    ) -> dict[str, str]:
        """Get request."""
        if params is None:
            params = {}

        url = self._build_url(endpoint)
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return data

    def post(self, endpoint: str, data=None, json=None) -> dict[str, str]:
        """Post request."""
        url = self._build_url(endpoint)
        response = self.session.post(url, data=data, json=json)
        response.raise_for_status()
        return response.json()

    def _build_url(self, endpoint: str) -> str:
        base_url = BASE_URL_PATTERN.sub("", self.base_url)
        endpoint = ENDPOINT_URL_PATTERN.sub("", endpoint)
        return base_url + "/" + endpoint


class PineconeAPIClient(APIClient):
    """API client for Pinecone.

    To make Pinecone requests, you must pass your API key in the header under
    ``Api-Key``.

    """

    def __init__(self, base_url: str, headers: Optional[dict[str, str]] = None):
        super().__init__(base_url, headers=headers)

    def get_paginated(
        self, endpoint: str, namespace: str, prefix: Optional[str] = None
    ) -> Optional[dict[str, str]]:
        """Get request for Pinecone API. Supports pagination with a token.

        For more details see: https://docs.pinecone.io/reference/list

        Args:
            endpoint: The endpoint.

            namespace: The namespace for the query. Useful to separate user data for example.

            prefix: A prefix for an ID. Used to identify titles for example.

        Returns:
            response:
        """
        params = {DatabaseConstants.KEY_PINECONE_NAMESPACE: namespace}

        if prefix:
            params.update({DatabaseConstants.KEY_PINECONE_PREFIX: prefix})

        response = self.get(endpoint=endpoint, params=params)
        # Field `pagination` exists if there is a next page.
        pagination = response.get("pagination")
        if not pagination:
            return response

        # Response has next page.
        vectors = response.get("vectors", [])
        namespace = response.get("namespace")

        while pagination:
            pagination_token = pagination.get("next")
            params.update({"paginationToken": pagination_token})
            response = self.get(endpoint=endpoint, params=params)
            vectors.extend(response.get("vectors", []))
            pagination = response.get("pagination")

        # Construct response with all vectors
        return {"vectors": vectors, "namespace": namespace}
