from abc import ABCMeta, abstractmethod
import logging
from logging import Logger
from typing import Optional


LOGGER_FILENAME = "app.log"


class AbstractApp(metaclass=ABCMeta):
    logger: Logger

    def __init__(self, log_level="DEBUG", file_logging=False):
        self.log_level = log_level
        self.file_logging = file_logging
        self.logger = self.initialize_logger(log_level)

    def initialize_logger(self, log_level) -> Logger:
        """Creates and configures a logger instance for console and file logging."""
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
    def query(self, query: str) -> Optional[str]:
        """Run a query against a database."""

    @abstractmethod
    def add(self, path: str) -> None:
        """Adds a document to the database."""

    @abstractmethod
    def delete(self, title: str) -> None:
        """Removes a document from the database."""
