class AppConstants:
    KEY_CONFIGURATION_PATH = "config_path"
    DEFAULT_CONFIG_FILE_PATH = "./configuration.yaml"


class LLMProviderConstants:
    KEY_AZURE_OPENAI_API_KEY = "AZURE_OPENAI_API_KEY"
    KEY_OPENAI_API_KEY = "OPENAI_API_KEY"


class ConfigurationConstants:
    # Database
    KEY_DATABASE = "database"
    KEY_DATABASE_BASE_PAH = "base_dir"
    KEY_DATABASE_NAME = "name"
    KEY_DOCUMENT_BASE_PATH = "document_base_path"
    KEY_NUMBER_SEARCH_RESULTS = "number_search_results"

    # Splitter
    KEY_SPLITTER = "splitter"
    KEY_CHUNK_SIZE = "chunk_size"
    KEY_CHUNK_OVERLAP = "chunk_overlap"

    # Embedding
    KEY_EMBEDDING = "embedding"
    KEY_EMBEDDING_MODEL = "model"

    # LLMs
    KEY_LLM = "llm"
    KEY_LLM_PROVIDER = "provider"
    KEY_LLM_MODEL = "model"
    LLM_PROVIDER_OPENAI = "openai"
    LLM_PROVIDER_AZUREOPENAI = "azure"
    KEY_AZURE_OPENAI_API_VERSION = "api_version"
    KEY_AZURE_OPENAI_AZURE_ENDPOINT = "endpoint"
