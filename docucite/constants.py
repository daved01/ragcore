class AppConstants:
    DATABASE_BASE_DIR = "data/database/"
    DATABASE_SEARCH_DEFAULT_K = 3
    DOCUMENT_BASE_PATH = "data/"
    NUMBER_OF_SEARCH_RESULTS = 5
    LLM_MODEL = "gpt-3.5-turbo"


class ConfigurationConstants:
    CONFIG_FILE_PATH = "./configuration.yaml"
    KEY_DATABASE_NAME = "database_name"
    DEFAULT_CHUNK_OVERLAP = 50
    DEFAULT_CHUNK_SIZE = 200
    DEFAULT_DATABASE_NAME = "chroma"
    KEY_CHUNK_OVERLAP = "chunk_overlap"
    KEY_CHUNK_SIZE = "chunk_size"
    KEY_DOCUMENT = "document"
