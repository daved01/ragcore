from abc import ABCMeta, abstractmethod
import logging
from logging import Logger
from typing import Optional

from ragcore.models.app_model import QueryResponse, TitlesResponse

LOGGER_FILENAME = "app.log"


class AbstractApp(metaclass=ABCMeta):
    """Abstract base app for RAG Core.

    Defines the required methods and sets up the logger.

    """

    logger: Logger

    def __init__(self, log_level="DEBUG", file_logging=False):
        self.log_level = log_level
        self.file_logging = file_logging
        self.logger = self.initialize_logger(log_level)

    def initialize_logger(self, log_level: str) -> Logger:
        """Creates and configures a logger instance for console and file logging.

        Sets the log level and defines the format of the log statements.

        Args:
            log_level: A string to set the log level.

        Returns:
            Logger: The logger instance for the app.

        """
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(module)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Create a file handler to log messages to a file
        if self.file_logging:
            file_handler = logging.FileHandler(LOGGER_FILENAME)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info(
                f"Logging to file {LOGGER_FILENAME} with log level {self.log_level}"
            )
        else:
            logger.info(f"Logging to terminal with log level {self.log_level}")
        return logger

    @abstractmethod
    def query(self, query: str, user: Optional[str] = None) -> QueryResponse:
        """Runs a query against a database."""

    @abstractmethod
    def add(self, path: str, user: Optional[str] = None) -> None:
        """Adds a document to the database."""

    @abstractmethod
    def delete(self, title: str, user: Optional[str] = None) -> None:
        """Removes a document from the database."""

    @abstractmethod
    def get_titles(self, user: Optional[str] = None) -> TitlesResponse:
        """Lists all titles owned by the user in the database, sorted in alphabetical order."""
