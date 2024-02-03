from langchain_community.document_loaders import PyPDFLoader

from ragcore.dto.document_dto import DocumentDTO
from ragcore.models.document_model import Document


class PDFLoader:
    """Class for the PDF loader.

    Atrributes:
        file_path: The path to the PDF file to be loaded.

    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_and_split(self, title: str) -> list[Document]:
        """Loads a PDF file with the specified title from the file path.

        The created metadata contains the field ``title`` which is taken from the arguments. Typically,
        the title is the file name without the file extension.

        Args:
            title: The title of the documents.

        Returns:
            A list of documents.

        """
        lang_loader = PyPDFLoader(self.file_path)
        lang_docs = lang_loader.load_and_split()

        # TODO: Must add book page, not pdf page! # pylint: disable=fixme
        for i, _ in enumerate(lang_docs):
            lang_docs[i].metadata["title"] = title
        return DocumentDTO.to_ragcore_list(lang_docs)
