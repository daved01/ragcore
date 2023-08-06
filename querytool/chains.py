"""Business logic to handle document parsing and retrieval."""

import logging
from logging import Logger
import os
import openai

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI


class ChainApp:
    """Chain app."""

    def __init__(
        self, llm_name="gpt-3.5-turbo", persist_directory="data/chroma_1500_150"
    ):
        self.openai_api_key = openai.api_key = os.environ["OPENAI_API_KEY"]
        self.persist_directory = persist_directory
        self.llm = ChatOpenAI(model_name=llm_name, temperature=0)
        self.vectordb = None
        self.pages = []  # TODO: Check type
        self.docs = []
        self.logger = self.get_logger()
        self.logger.info(
            f"Initialized app. Using persisted store {self.persist_directory.split('/')[1]}"
        )

    def get_logger(self, file_logging=False) -> Logger:
        """Creates and configures logger instance for console and file logging."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Create a file handler to log messages to a file
        if file_logging:
            file_handler = logging.FileHandler("app.log")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        return logger

    def load_pdf(self, path: str, document_title: str) -> None:
        """Loads a PDF"""
        loader = PyPDFLoader(path)
        self.pages = loader.load_and_split()

        # Add document title
        for i in range(len(self.pages)):
            self.pages[i].metadata["title"] = document_title
        self.logger.info(
            f"Added title `{document_title}` to metadata of {len(self.pages)} pages."
        )
        self.logger.info(
            f"Loaded pdf file from path {path}. Loaded {len(self.pages)} pages."
        )

    # TODO: Optimize
    def split_document(self, chunk_size, chunk_overlap) -> None:
        """Splits a document."""
        self.logger.info("Splitting documents ...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        if not self.pages:
            raise ValueError("Pages not defined. Please call `load_pdf` first.")
        self.docs = splitter.split_documents(self.pages)
        self.logger.info(f"Created {len(self.docs)} documents.")

    # TODO: How does this work?
    def store(self, dry_run=False) -> None:
        """Stores embeddings in the vector database."""
        embedding = OpenAIEmbeddings()
        if not self.docs:
            raise ValueError("Docs not assigned.")
        self.vectordb = Chroma.from_documents(
            documents=self.docs,
            embedding=embedding,
            persist_directory=self.persist_directory,
        )
        self.logger.info(
            f"Stored {self.vectordb._collection.count()} collections in vector database."
        )

        if not dry_run:
            self.vectordb.persist()

    def load_embeddings(self) -> None:
        """Load embeddings from database"""
        embedding = OpenAIEmbeddings()
        self.vectordb = Chroma(
            persist_directory=self.persist_directory, embedding_function=embedding
        )
        self.logger.info(f"Loaded embeddings from path: {self.persist_directory}.")

    def build_prompt_template(self) -> PromptTemplate:
        """Builds a prompt."""
        template = """
        Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer. 
        Mention the page on which the topic in the answer is mentioned if a page is available, 
        otherwise do not mention a page. 
        Ask if the user has further question regarding the topic.
        {context}
        Question: {question}
        Helpful Answer:"""
        return PromptTemplate.from_template(template)

    def query(self, prompt: str, question: str) -> str:
        """Queries the tool and returns the answer."""
        qa_chain = RetrievalQA.from_chain_type(
            self.llm,
            retriever=self.vectordb.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

        result = qa_chain({"query": question})
        self.logger.info(f"Metadata: {qa_chain.metadata}")
        # return result
        return result["result"]
