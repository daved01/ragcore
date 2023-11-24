# Docucite

[![Unit Tests](https://github.com/daved01/docucite/workflows/code-check-main.yml/badge.svg)](https://github.com/daved01/docucite/workflows/code-check-main.yml)
![GitHub](https://img.shields.io/github/license/daved01/docucite)
[![GitHub Actions](https://github.com/daved01/docucite/workflows/code-check-main/badge.svg)](https://github.com/daved01/docucite/actions)

Docucite is built to help you to start getting insights from your documents through natural language in less than one minute and to simplify customization as a base for your custom applications.

It uses Langchain, OpenAI, and Chroma. Want to use a different LLM or Vector database? Adding these components is made easy, so you can quickly iterate with for example different LLMs, and build an application to your requirements on top.

Worried about privacy? By using a local database, only relevant text extracts are exposed to the languge model (TODO: What about the embedding?). Furthermore, adding a different language model is made easy, so you can for example use a hosted LLM.

# Quick start

Before installation, make sure you have at least Python 3.10 installed. Additionally, for the default configuration you need an OpenAI [API key](https://platform.openai.com/api-keys) in your environment variables with the name `OPENAI_API_KEY`.

## Installation

To install, just run `pip install -r requirements.txt`. Make sure you have at least Python 3.10 installed.

## Usage

If you want to quickly add a pdf file and start searching it, add it to the path `data`, and add the name of the file in the `configuration.yaml` file. Then, just run the cli application with `python -m docucute.cli` and follow the instructions to create a new database. Once that is done, you can start typing in a question in the CLI, or open the web interface with `uvicorn fastapi_app:app --reload`.

To learn more about how the app works and how you can customize it, read on.

## Advanced configuration

The app has a default configuration so you can start quickly. You can adjust the configuration to your needs with the `configuration.yaml` file in the root. The file looks like this:

```
database_name: "chroma"
document: "Python summary.pdf"
chunk_size: 150
chunk_overlap: 50
```

The field `database_name` is the name of the vector database. The database will be created in the folder `data/database` if it does not already exists. Otherwise, the existing database is loaded. The final name of the database will also include the chunk size and chunk overlap. The final database name is in the format `<database_name>_<chunk_size>_<chunk_overlap>`.

The second field `document` is the name of the document you want to load into the database. The document is expected in the base path `data`. Currently supported document types are: `pdf`.

The `chunk_size` and `chunk_overlap` are two parameters which determine how the document is processed before it is added into the database. These two parameters are very important as they determine the performance of your application. Chunk size is the length of the chunks into which the document is split. For example, a chunk size of 87 would add this whole sentence if it were the first one. (TODO: verify). But it is likely that the information you are interested in is spread over multiple sentences. Consequently, you want to also consider what comes before and after. This is exactly what `chunk_overlap` does. It determines how many characters of the previous document is repeated in the next one. For more information about this topic see for example: TODO: Add source.

In general, a larger chunk size allows for more context at the expense of processing time. A larger overlap

# How it works

The following image shows the components.

TODO: Add image
[!image]

# Development

First, set up a development environment by installing the development dependencies with `pip install -r requirements_dev.txt`.

## App structure

The project is structured as follows

```
├── data
    └── <your-document>
    └── ...
    └── database
        └── <your-database>
├── docucite
    └── app
    └── dto
    └── models
    └── services
    └── constants.py
    └── ...
├── static
    └── index.html
├── tests
    └── unit
        └── ...
├── configuration.yaml
├── ...
```

The app in the source folder `docucite` is structured into the layers `app`, `dto`, `models`, and `services`.

## How to: customization

This section shows how to customize and extend the app.

### Changing defaults

In the previous section it was shown how to configure the app with the configuration file. If anything is missing, defaults are used (with the exception of the document name). These defaults, along with other constants, are defined in the file `constants.py`. Here you can for example change the base path for the database, or point to a different configuration file.

### Add a large language model

To add a new LLM, subclass the `LLModel` in `models/llm_model.py` and return the model in the `_get_llm()` method. Then, this model is used by the `LLMService` in `services/llm_service.py`.

### Add embedding

To create a vector out of the input data so that it can be stored in the vector database, the OpenAI embedding is used by default in the `DatabaseService`. To change the embedding, subclass the `EmbeddingModel` in `models/embedding_model.py`.

### Add new database

To add a new database, subclass the `VectorDataBaseModel` and use it in the `DatabaseService`.

### Add custom UI

The UI is defined in `static/index.html`. It uses the fast api endpoints which you can use to add a different frontend.

# Contributing

Contributions in the form of pull requests are highly welcome. To keep the codebase maintainable, please follow a few guidelines regarding code and commit messages. In short:

+ Add tests for new code

+ Pass quality checks

+ Keep pull requests small

+ Use Conventional Commits

## Code quality

Before opening a PR, please make sure that your code in `docucite` passes all quality checks. You can check your code before opening a PR with the commands

```
pylint docucite/
black docucite/
mypy docucite/
```

New code must be covered by tests and documented with comments where applicable. In most cases type hints should be added as well. And keep pull requests small by changing only relevant code, as this simplifies reviews and simplifies debugging if something goes wrong in the future.

## Conventional Commits

Please use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) with the following commit elements:

**feat:** A "feature" type commit indicates the introduction of a new feature or enhancement to the project.

**fix:** A "fix" type commit indicates the correction of a bug or issue in the codebase.

**chore:** A "chore" commit is used for routine maintenance or housekeeping tasks, such as dependency updates, build system modifications, or other non-functional changes.

**docs:** A "documentation" commit is used when you make changes or additions to documentation, such as README files or inline code comments.

**build:** A "build" commit is used when you make changes related to the build system, configuration, or build tooling.

Commits in PRs will be squashed into one commit. By using conventional commits and squashing a `Changelog` file is unecessary.

# License

The project comes with a MIT license. You are free to use and modify the code in your applications.

# Support

If you like this work and you find it helpful, I would appreciate your support [here](https://www.paypal.com/donate/?hosted_button_id=23YUGLRRTNDMS). Your contribution enables me to continue to work on this project.
