from langchain.embeddings import OpenAIEmbeddings
from langchain.schema.document import Document


class VectorDataBaseModel:
    def __init__(self, persist_directory: str, embedding_function: OpenAIEmbeddings):
        self.persist_directory = persist_directory
        self.embedding_function = embedding_function

    def _init_chroma(self):
        pass

    def _get_embedding(self):
        pass

    def similarity_search(self):
        pass
