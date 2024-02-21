from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfiguration:
    provider: str
    number_search_results: int
    base_path: Optional[str]
    base_url: Optional[str]


@dataclass
class SplitterConfiguration:
    chunk_overlap: int
    chunk_size: int


@dataclass
class EmbeddingConfiguration:
    provider: str
    model: str
    endpoint: Optional[str]
    api_version: Optional[str]


@dataclass
class LLMConfiguration:
    provider: str
    model: str
    endpoint: Optional[str]
    api_version: Optional[str]


@dataclass
class AppConfiguration:
    database_config: DatabaseConfiguration
    splitter_config: SplitterConfiguration
    embedding_config: EmbeddingConfiguration
    llm_config: LLMConfiguration
