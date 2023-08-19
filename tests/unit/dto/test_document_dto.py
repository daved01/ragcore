from docucite.dto.document_dto import DocumentDTO

from tests.unit.services import DocuciteTestSetup


class TestDocumentDTO(DocuciteTestSetup):
    def test_to_docucite(self, mock_lang_documents):
        docs = []
        for document in mock_lang_documents:
            dto = DocumentDTO(
                page_content=document.page_content, metadata=document.metadata
            )
            docs.append(dto.to_docucite())
        assert len(docs) == len(mock_lang_documents)
        for i, doc in enumerate(docs):
            assert doc.page_content == mock_lang_documents[i].page_content
            assert doc.metadata == mock_lang_documents[i].metadata

    def test_to_langchain(self, mock_documents):
        docs = []
        for document in mock_documents:
            dto = DocumentDTO(
                page_content=document.page_content, metadata=document.metadata
            )
            docs.append(dto.to_langchain())
        assert len(docs) == len(mock_documents)
        for i, doc in enumerate(docs):
            assert doc.page_content == mock_documents[i].page_content
            assert doc.metadata == mock_documents[i].metadata
