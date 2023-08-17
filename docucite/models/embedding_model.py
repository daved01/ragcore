from langchain.embeddings import OpenAIEmbeddings


class Embedding:
    """Wrapper for embeddings."""

    def __init__(self, model: str = "text-embedding-ada-002"):
        self.model = model
        self.openai_embedding = OpenAIEmbeddings(model=model)

    def embed_documents(self, texts: str, chunk_size: int = None) -> list[list[float]]:
        return self.openai_embedding.embed_documents(texts=texts, chunk_size=chunk_size)

    def embed_query(self, text: str) -> list[float]:
        return self.openai_embedding.embed_query(text=text)
