+ Add cool logo

+ Add header links for:
My website
+ Badges for testing, license

# Document Question Tool

# Features

This is a tool to chat with data out of box, which let's you start querying your data in less than two minutes. It uses langchain, OpenAI, and Chroma. With this configuration you can get it running within less than a minute. Want to use a different LLM or Vector database? Adding these components is made easy, so you can quickly iterate with for example different LLMs, and build an application to your requirements on top.

Supports openAI

Extensions are easy. Add a different model say Azure, integrate it into your application with minimal modifications, add it to your app with the simple api.

There is a command line option and a UI option. To use the latter, run `uvicorn fastapi_app:app --reload`.

To run the command line option, run `python -m docucite.cli`.

## Quick start

To install, just run `pip install -r requirements.txt`. If you want to develop, also run `pip install -r requirements_dev.txt`. Supported Python versions: >= 3.8

Then, if you just want to quickly add a pdf file and start searching it, add it to the path `data`, and add the name of the file in the `configuration.yaml` file. Then just run the cli application and follow the instructions to create a new database. Once that is done, you can start typing in a question in the CLI, or open the web interface.

To learn more about how the app works and how you can customize it, read on.

## Getting started

### Configuration

To use the app with the default OpenAI models, you need an OpenAI API key in the environment variables `OPENAI_API_KEY`.

Overall, for the configuration of the app two files are important. The file to configure the app from a user's perspective is the `configuration.yaml` file in the root of the project. It is explained in detail below. A second file is the `constants.py` file, which contains constants that are used throughout the code. For example, the base path for the data is defined here, as well as the names of the keys of the configuration file.

Configuration of the app is done with `configuration.yaml` file in the root. The file looks like this:

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

### Using the cli interface

Once you have set an OpenAI key, you can use the app with the cli interface by running `python -m docucute.cli`.

### Using the web app interface

## Development

### App structure

The app is structured into the layers `api`, `app`, `services`, and `model`.

The structure is

```
├── docs
├── docucite
├── notes
├── static
├── tests
    └──

```

## Development

Install dependencies with `pip install -r requirements_dev.txt`.

All code in the main folder `docucite` must be tested and of high quality.

## Code quality

Before submitting a PR, make sure the code in `docucite` is clean. We use the three tools:

`pylint docucite/`
`black docucite/`
`mypy docucite/`

## Contributing

Quality checks

Clean code

All features must come with at least unit tests

## License

Comes with a ??? license. You are free to use and modify the code in your applications

## Support

If you like this work, I'd appreciate your support here. Every contribution counts
