from langchain_community.document_loaders import PyPDFLoader

from docucite.dto.document_dto import DocumentDTO
from docucite.models.document_model import Document


class PDFLoader:
    """Wrapper for PDF loader."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_and_split(self) -> list[Document]:
        lang_loader = PyPDFLoader(self.file_path)
        lang_docs = lang_loader.load_and_split()
        return DocumentDTO.to_docucite_list(lang_docs)
