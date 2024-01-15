class APIConstants:
    KEY_AZURE_OPENAI_API_KEY = "AZURE_OPENAI_API_KEY"
    KEY_OPENAI_API_KEY = "OPENAI_API_KEY"


class AppConstants:
    DATABASE_BASE_DIR = "data/database/"
    DATABASE_SEARCH_DEFAULT_K = 3
    DOCUMENT_BASE_PATH = "data/"
    NUMBER_OF_SEARCH_RESULTS = 5
    OPENAI_EMBEDDING = "text-embedding-ada-002"


class ConfigurationConstants:
    CONFIG_FILE_PATH = "./configuration.yaml"
    DEFAULT_CHUNK_OVERLAP = 256
    DEFAULT_CHUNK_SIZE = 1024
    DEFAULT_DATABASE_NAME = "chroma"
    KEY_LLM_MODEL = "llm_model"
    KEY_CHUNK_OVERLAP = "chunk_overlap"
    KEY_CHUNK_SIZE = "chunk_size"
    KEY_DATABASE_NAME = "database_name"
    KEY_DOCUMENT = "document"
    KEY_LLM_PROVIDER = "llm_provider"

    KEY_AZURE_OPENAI_API_VERSION = "azure_api_version"
    KEY_AZURE_OPENAI_AZURE_ENDPOINT = "azure_endpoint"

    LLM_PROVIDER_OPENAI = "openai"
    LLM_PROVIDER_AZUREOPENAI = "azure"
    DEFAULT_LLM_PROVIDER = LLM_PROVIDER_OPENAI
