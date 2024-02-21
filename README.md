# RAG Core

<p align="center">
  <a href="https://www.python.org/downloads/release/python-310/"><img src="https://img.shields.io/badge/python-3.10-green.svg" alt="Python 3.10"></a>
  <a href="https://www.python.org/downloads/release/python-311/"><img src="https://img.shields.io/badge/python-3.11-green.svg" alt="Python 3.11"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
  <a href="https://pypi.org/project/ragcore"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/ragcore?color=blue"></a>
  <img src="https://github.com/daved01/ragcore/actions/workflows/code-check-main.yml/badge.svg" alt="GitHub CI">
</p>

A Retrieval-Augmented Generation library with a CLI interface. Build RAG applications with just a few commands and a configuration file.

## Supported setups

| Databases               | LLMs           | Embeddings     | Document types  |
| ----------------------- | -------------- | -------------- | --------------- |
| Chroma (local)          | OpenAI         | OpenAI         | PDF             |
| Pinecone (remote)       | AzureOpenAI    | AzureOpenAI    |                 |

For more details see the [documentation](https://daved01.github.io/ragcore/).

# Installation

To install, run

```bash
pip install ragcore
```

or clone and build from source

```bash
git clone https://github.com/daved01/ragcore.git
cd ragcore
pip install .
```

If everything worked, running

```bash
ragcore -h
```

should show you some information about `ragcore`.

# A Simple Example

To build an application with OpenAI or AzureOpenAI LLMs and embeddings, and a local database, first set your OpenAI [API key](https://platform.openai.com/api-keys) as described [here](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key):

```bash
export OPENAI_API_KEY=[your token]
```

Then, create a config file `config.yaml` like this in the root of your project:

```bash
database:
  provider: "chroma"
  number_search_results: 5
  base_dir: "data/database"

splitter:
  chunk_overlap: 256
  chunk_size: 1024

embedding:
  provider: "openai"
  model: "text-embedding-model"

llm:
  provider: "openai"
  model: "gpt-model"

```

And finally, create your application using this config file:

```python
from ragcore import RAGCore


app = RAGCore() # pass config=<path-to-config.yaml> if not in root

# Upload a document "My_Book.pdf"
app.add(path="My_Book.pdf")

# Now you can ask questions
answer = app.query(query="What did the elk say?")

print(answer.content)

# List the document's title and content on which the response is based
for doc in answer.documents:
  print(doc.title, " | ", doc.content)

# List all documents in the database
print(app.get_titles())

# You can delete by title
app.delete(title="My_Book")
```

And that's it! For more information, as well as an overview of supported integrations check out the [documentation](https://daved01.github.io/ragcore/).
