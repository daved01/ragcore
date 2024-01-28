from ragcore.dto.document_dto import DocumentDTO
from tests.unit.services import RAGCoreTestSetup


class TestDocumentDTO(RAGCoreTestSetup):
    def test_to_ragcore(self, mock_lang_documents):
        docs = DocumentDTO.to_ragcore_list(mock_lang_documents)
        assert len(docs) == len(mock_lang_documents)
        for i, doc in enumerate(docs):
            assert doc.page_content == mock_lang_documents[i].page_content
            assert doc.metadata == mock_lang_documents[i].metadata

    def test_to_langchain(self, mock_documents):
        docs = DocumentDTO.to_langchain_list(mock_documents)
        assert len(docs) == len(mock_documents)
        for i, doc in enumerate(docs):
            assert doc.page_content == mock_documents[i].page_content
            assert doc.metadata == mock_documents[i].metadata
