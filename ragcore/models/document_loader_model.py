from langchain_community.document_loaders import PyPDFLoader

from ragcore.dto.document_dto import DocumentDTO
from ragcore.models.document_model import Document


class PDFLoader:
    """Wrapper for PDF loader."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_and_split(self, title: str) -> list[Document]:
        lang_loader = PyPDFLoader(self.file_path)
        lang_docs = lang_loader.load_and_split()

        # TODO: Must add book page, not pdf page! # pylint: disable=fixme
        for i, _ in enumerate(lang_docs):
            lang_docs[i].metadata["title"] = title
        return DocumentDTO.to_ragcore_list(lang_docs)
