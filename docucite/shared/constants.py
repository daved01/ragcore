class AppConstants:
    """Constants for the app."""

    KEY_CONFIGURATION_PATH = "config_path"
    KEY_LOGGER_FLAG = "verbose_logger"
    DEFAULT_CONFIG_FILE_PATH = "./configuration.yaml"


class ConfigurationConstants:
    """Constants for the configuration file."""

    # Database
    KEY_DATABASE = "database"
    KEY_DATABASE_BASE_PATH = "base_dir"
    KEY_DATABASE_PROVIDER = "provider"
    KEY_DATABASE_TYPE = "type"
    KEY_NUMBER_SEARCH_RESULTS = "number_search_results"

    # Splitter
    KEY_SPLITTER = "splitter"
    KEY_CHUNK_SIZE = "chunk_size"
    KEY_CHUNK_OVERLAP = "chunk_overlap"

    # Embedding
    KEY_EMBEDDING = "embedding"
    KEY_EMBEDDING_PROVIDER = "provider"
    KEY_EMBEDDING_MODEL = "model"
    KEY_EMBEDDING_AZURE_OPENAI_API_VERSION = "api_version"
    KEY_EMBEDDING_AZURE_OPENAI_AZURE_ENDPOINT = "endpoint"

    # LLMs
    KEY_LLM = "llm"
    KEY_LLM_PROVIDER = "provider"
    KEY_LLM_MODEL = "model"
    LLM_PROVIDER_OPENAI = "openai"
    LLM_PROVIDER_AZUREOPENAI = "azure"
    KEY_AZURE_OPENAI_API_VERSION = "api_version"
    KEY_AZURE_OPENAI_AZURE_ENDPOINT = "endpoint"


class DataConstants:
    """Constants for the data model."""

    KEY_TITLE = "title"
    KEY_PAGE = "page"


class DatabaseConstants:
    """Constants for database models and service."""

    PROVIDER_CHROMA = "chroma"
    KEY_CHROMA_DOCUMENTS = "documents"
    KEY_CHROMA_METADATAS = "metadatas"


class EmbeddingConstants:
    """Constants for embedding models."""

    KEY_AZURE_OPENAI_API_KEY = "AZURE_OPENAI_API_KEY"
    PROVIDER_AZURE_OPENAI = "azure"
    PROVIDER_OPENAI = "openai"


class LLMProviderConstants:
    """Constants for LLM models and service."""

    KEY_AZURE_OPENAI_API_KEY = "AZURE_OPENAI_API_KEY"
    KEY_OPENAI_API_KEY = "OPENAI_API_KEY"
