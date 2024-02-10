from ragcore.dto.document_dto import DocumentDTO
from tests.unit.services import RAGCoreTestSetup


class TestDocumentDTO(RAGCoreTestSetup):
    def test_to_ragcore(self, mock_lang_documents):
        docs = []
        for lang_document in mock_lang_documents:
            dto = DocumentDTO(
                content=lang_document.page_content,
                title=lang_document.metadata.get("title", ""),
                metadata=lang_document.metadata,
            )
            doc = dto.to_ragcore()
            docs.append(doc)

        for ind, doc in enumerate(docs):
            assert doc.content == mock_lang_documents[ind].page_content
            assert doc.metadata == mock_lang_documents[ind].metadata

    def test_to_langchain(self, mock_documents):
        docs = []
        for document in mock_documents:
            dto = DocumentDTO(
                content=document.content,
                title=document.title,
                metadata=document.metadata,
            )
            doc = dto.to_langchain()
            docs.append(doc)

        for ind, doc in enumerate(docs):
            assert doc.page_content == mock_documents[ind].content
            assert doc.metadata == mock_documents[ind].metadata

    def test_to_ragcore_list(self, mock_lang_documents):
        docs = DocumentDTO.to_ragcore_list(mock_lang_documents)
        assert len(docs) == len(mock_lang_documents)
        for i, doc in enumerate(docs):
            assert doc.content == mock_lang_documents[i].page_content
            assert doc.metadata == mock_lang_documents[i].metadata
