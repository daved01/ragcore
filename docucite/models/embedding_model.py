from typing import Optional
from langchain_community.embeddings import OpenAIEmbeddings


class Embedding:
    """Wrapper for embeddings."""

    def __init__(self, model: str):
        self.model = model
        self.openai_embedding = OpenAIEmbeddings(model=model, client=None)

    def embed_documents(
        self, texts: list[str], chunk_size: Optional[int] = None
    ) -> list[list[float]]:
        return self.openai_embedding.embed_documents(texts=texts, chunk_size=chunk_size)

    def embed_query(self, text: str) -> list[float]:
        return self.openai_embedding.embed_query(text=text)
