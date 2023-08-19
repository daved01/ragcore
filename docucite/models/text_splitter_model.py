from langchain.text_splitter import RecursiveCharacterTextSplitter

from docucite.models.document_model import Document

# from docucite.models.document_loader_model import D


# TODO:
class TextSplitterModel:
    """Wrapper for TextSplitter."""

    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_documents(self, documents: list[Document]) -> list[Document]:
        pass
