from dataclasses import dataclass
from typing import Optional, Sequence

from ragcore.models.document_model import Document


@dataclass
class QueryResponse:
    """Model for query responses.

    Attributes:
        content: String with the response, None if no response could be generated.

        documents: Sequence of documents on which the response is based on. Empty list if response is None.

        user: An optional string to identify a user.

    """

    content: Optional[str]
    documents: Sequence[Optional[Document]]
    user: Optional[str]


@dataclass
class TitlesResponse:
    """Model for document title responses.

    Attributes:
        user: The owner of the titles.

        contents: The list of title strings.
    """

    user: Optional[str]
    contents: list[Optional[str]]
