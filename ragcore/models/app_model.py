from dataclasses import dataclass
from typing import Optional, Sequence

from ragcore.models.document_model import Document


@dataclass
class QueryResponse:
    """Model for query responses.

    Attributes:
        content: String with the response, None if no response could be generated.

        documents: Sequence of documents on which the response is based on. Empty list if response is None.

    """

    content: Optional[str]
    documents: Sequence[Optional[Document]]
