from langchain.document_loaders import PyPDFLoader

from docucite.dto.document_dto import DocumentDTO
from docucite.models.document_model import Document


class PDFLoader:
    """Wrapper for PDF loader."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_and_split(self) -> list[Document]:
        lang_loader = PyPDFLoader(self.file_path)
        lang_docs = lang_loader.load_and_split()

        docs = []
        for lang_doc in lang_docs:
            doc_dto = DocumentDTO(
                page_content=lang_doc.page_content, metadata=lang_doc.metadata
            )
            docs.append(doc_dto.to_docucite())

        return docs
