# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.0.4] - 2024-03-04

### Fixed

- Handling of titles in Pinecone database has been updated. Pinecone does not offer a simple way to retrieve metadata to get a list of titles. To overcome this, titles are encoded in record prefixes by ragcore. Titles can be case-sensitive, and can contain spaces now.

## [1.0.3] - 2024-03-02

### Added

- Pinecone uploads are now chunked to handle larger file sizes. The Pinecone recommendation is 100 records per batch [https://docs.pinecone.io/docs/upsert-data].

- Pinecone upload throughput was increased by using Pinecone's asynchronous upload option using `pool_threads`.

### Removed

- Document titles have been removed from log outputs for increased privacy.

## [1.0.2] - 2024-02-21

### Added

- Pinecone database is now supported. To use it, select `pinecone` in the config file, add your Pinecone `base_url`, and done!

### Changed

- Internally, a model is now used for the configuration of the app, replacing the dictionaries.

## [1.0.1] - 2024-02-13

### Fixed

- When trying to access a Chroma collection which does not exist, the collection is now automatically created.

## [1.0.0] - 2024-02-11

### Added

- New `query` response object `QueryResponse` contains information about the sources on which the response is based on. You can now extract the titles as well as the document chunks from the response.
- The option to specify an identifier for a `user` with all app-level requests, to support multiple users.
- A `get_titles()` method on the app level to get a string list of all titles owned by a user in the database.

### Changed

- Changed the return type of the query method to return a `QueryResponse` object instead of an optional string. To get the response string as before, call `response.content` on the query response.

## [0.0.8] - 2024-02-04

### Fixed

- Fixed app import

## [0.0.7] - 2024-02-04

### Added

- Added documentation
- Improved docstrings

## [0.0.6] - 2024-01-29

### Added

- Verbose logger flag
- Azure OpenAI embeddings
- Azure OpenAI LLMs
