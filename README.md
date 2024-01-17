# Docucite

<p align="center">
  <a href="https://www.python.org/downloads/release/python-310/"><img src="https://img.shields.io/badge/python-3.10-green.svg" alt="Python 3.10"></a>
  <a href="https://www.python.org/downloads/release/python-311/"><img src="https://img.shields.io/badge/python-3.11-green.svg" alt="Python 3.11"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
  <img src="https://github.com/daved01/docucite/actions/workflows/code-check-main.yml/badge.svg" alt="example workflow">
</p>

Docucite is designed to help you to start getting insights from your documents through natural language within minutes and to simplify customization as a base for your custom applications.

Leveraging Langchain, OpenAI, and Chroma, Docucite allows seamless integration of alternative Large Language Models (LLM) or Vector databases. This flexibility enables rapid iteration, empowering you to experiment with various LLMs and construct applications tailored to your specific needs using the CLI or API interfaces.

## Quick start

Before installation, make sure you have at least Python 3.10 installed. Additionally, for the default configuration you need an OpenAI [API key](https://platform.openai.com/api-keys) in your environment variables with the name `OPENAI_API_KEY` as described [here](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key).

### Installation

To install, just run `pip install -r requirements.txt`. Make sure you have at least Python 3.10 installed.

### Usage

To add a PDF file for querying, place it in the `data` directory (create it or run the CLI tool). Run the CLI application with `python -m docucute.cli` and follow the prompts to generate a new database, and upload your PDF file by entering its name when prompted. Once completed, you can enter questions in the CLI or launch the web interface using `uvicorn docucite.api:fastapi --reload`.

Explore the subsequent sections for an in-depth comprehension of the app's features and customization possibilities.

### Advanced configuration

The app has a default configuration so you can start quickly. You can adjust the configuration to your needs with the `configuration.yaml` file in the root. The file looks like this by default:

```bash
database:
  base_dir: "data/database"
  name: "chroma"
  document_base_path: "data"
  number_search_results: 5

splitter:
  chunk_overlap: 256
  chunk_size: 1024

embedding:
  model: "text-embedding-ada-002"

# OpenAI
llm:
  provider: "openai"
  model: "gpt-3.5-turbo"

# AzureOpenAI
# llm:
#   provider: "azure"
#   model: "gpt-3.5-turbo"
#   endpoint: ""
#   api_version: ""

```

The `configuration.yaml` file contains the keys `database`, `splitter`, `embedding`, and `llm` and is designed to serve as a starting configuration.

#### Database

In the `database` section, the field `name` is the name of the vector database. The database will be created in the folder under `base_dir` if it does not already exists. Otherwise, the existing database is loaded. The final name of the database will also include the chunk size and chunk overlap. The final database name is in the format `<database_name>_<chunk_size>_<chunk_overlap>`.

#### Splitter

In the `splitter` part the parameters for splitting of documents are specified. The `chunk_size` and `chunk_overlap` are two parameters which determine how the document is broken down before it is added to the database. These two parameters are very important as they determine the performance of your application by impacting the relevance of the documents that are retrieved given an input.

The chunk size represents the number of tokens in each document chunk. Optimal selection depends on your documents and the chosen embedding model. Strive for a chunk size that produces chunks that in isolation a human would understand, while minimizing the length to keep cost for LLM request in check (multiple relevant chunks are send to the LLM, see below).

Chunk overlap is how much overlap there is between adjacent chunks. Overlap is useful to not miss any information that is potentially on the edge of a chunk or spread over multiple chunks. The trade-off is some redudancy in the database and increased computation.

For more information about text splitting see for example [here](https://www.pinecone.io/learn/chunking-strategies/).

#### LLM

Currently, OpenAI and AzureOpenAI are supported. By default `openai` is used as an llm provider, as you can see in the config file. Make sure to have your API key set in the environment variable `OPENAI_API_KEY`.

To use AzureOpenAI, uncomment the AzureOpenAI part and remove the OpenAI part. Please note that AzureOpenAI requires you to provide an `endpoint` and an `api_version`. Additionally, you must have an API key set in the environment variable `AZURE_OPENAI_API_KEY`.

## How it works

The system consists of a few basic components.

![image](/docs/architecture.png)

**Adding documents**

To add a document, the document is split into overlapping chunks first. Then, these chunks are vectorized using the embedding, before these vectors, along with the contents, are added to the database.

![image](/docs/adding_documents.png)

**Querying documents**

A new query triggers the creation of a vector through embedding. This vector is used to calculate a similarity score with vectors in the database, identifying related documents that are subsequently retrieved. Using these documents and the initial query, a prompt is constructed and forwarded to the Language Model (LLM) to generate an answer, which is then returned to the user.

![image](/docs/querying.png)

## Development

First, set up a development environment by installing the development dependencies with `pip install -r requirements_dev.txt`.

### App structure

The project is structured as follows

```bash
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
    └── api.py
    └── cli.py
    └── constants.py
    └── ...
├── docs
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

### Changing defaults

In the previous section, we covered configuring the app using the configuration file. Any missing configurations default to default values (excluding the document name). These defaults, alongside other constants, are specified in the `constants.py` file. In this file, you have the flexibility to modify parameters such as the base path for the database or point to an alternative configuration file.

### Supported models

The app supports OpenAI models and Azure OpenAI models. For the former, a valid API key has to be in the environment with the name `OPENAI_API_KEY`. For Azure deployments, the environment variable `AZURE_OPENAI_API_KEY` is required.

### Add a large language model

To add a new LLM, subclass the `LLModel` in `models/llm_model.py` and return the model in the `_get_llm()` method. Then, this model is used by the `LLMService` in `services/llm_service.py`.

### Add embedding

To create a vector out of the input data so that it can be stored in the vector database, the OpenAI embedding is used by default in the `DatabaseService`. To change the embedding, subclass the `EmbeddingModel` in `models/embedding_model.py`.

The default [OpenAI embedding](https://openai.com/blog/new-and-improved-embedding-model) is `text-embedding-ada-002`.

### Add new database

To add a new vector database, subclass the `VectorDataBaseModel` and use it in the `DatabaseService`. To learn more about what a vector database is and how it works, check out for example [this](https://www.pinecone.io/learn/vector-database/) great post by the Pinecone team.

### Add custom UI

The UI is defined in `static/index.html`. It uses the fast api endpoints which are defined in `docucite/api.py`.

### Change prompt

Using the retrieved information from the vector database, the information is concatenated to a string and along with the question passed into the `PromptGenerator` in `models/prompt_model.py`. This prompt can be changed and it might be worth to experiment with variations.

### Further changes

The changes described so far swap out existing components. Further optimization could for example include changing the similarity measure used to retrieve vectors from the database, or using a different text splitting method in `TextSplitterService` in `services/text_splitter_service.py` (currently langchain's `RecursiveCharacterTextSplitter` is used).

## Contributing

Contributions in the form of pull requests are highly welcome. To keep the codebase maintainable, please follow a few guidelines regarding code and commit messages. In short:

+ Add tests for new code

+ Pass quality checks

+ Keep pull requests small

+ Use Conventional Commits

### Code quality

Before opening a PR, please make sure that your code in `docucite` passes all quality checks. You can check your code before opening a PR with the commands

```bash
pylint docucite/
black docucite/
mypy docucite/
```

New code must be covered by tests and documented with comments where applicable. In most cases type hints should be added as well. And please keep pull requests small by changing only relevant code, as this simplifies reviews and debugging if something goes wrong in the future.

### Conventional Commits

Please use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) with the following commit elements:

**feat:** A "feature" type commit indicates the introduction of a new feature or enhancement to the project.

**fix:** A "fix" type commit indicates the correction of a bug or issue in the codebase.

**chore:** A "chore" commit is used for routine maintenance or housekeeping tasks, such as dependency updates, build system modifications, or other non-functional changes.

**docs:** A "documentation" commit is used when you make changes or additions to documentation, such as README files or inline code comments.

**build:** A "build" commit is used when you make changes related to the build system, configuration, or build tooling.

Commits in PRs will be squashed into one commit. By using conventional commits and squashing a `Changelog` file is unecessary.

## License

The project is licensed under the MIT license, granting you the freedom to use and modify the code for your applications.

## Support

If you find this work valuable and helpful, I would greatly appreciate your support. Consider contributing [here](https://www.paypal.com/donate/?hosted_button_id=23YUGLRRTNDMS) to help sustain and advance the development of this project. Your generosity enables me to dedicate more time and effort to enhance the project further. Thank you for your support!
