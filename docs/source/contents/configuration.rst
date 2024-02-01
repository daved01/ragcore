.. _configuration:

**********************
Configuration
**********************

While the previous section :ref:`first_app` demonstrated a basic configuration, this section elaborates on the configuration options.

As demonstrated in :ref:`first_app`, an example configuration file ``config.yaml`` looks like this:


.. code-block:: yaml

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

The top-level keys correspond to component families, while the lower-level keys allow you to select a specific component or set values for that component. Let's walk through the keys step-by-step. 

For a list of supported components, refer to the section :ref:`supported_components`.


Database
=================
**Key** ``database``

``number_search_results`` - The number of chunks which are returned by the database and passed to the LLM in the prompt. A higher number can lead to more detailed answers, since more context is available, but the risk is that more irrelevant documents are retrieved, which reduces the quality of the answer.

``base_dir`` - The directory in which the local database will be persisted. If this directory does not exist it will be created.


Splitter
=================
**Key** ``splitter``

``chunk_size`` - Represents the number of tokens in each document chunk. The optimal selection depends on your documents and the chosen embedding model. Strive for a chunk size that produces chunks that in isolation a human would understand, while minimizing the length to keep cost for LLM request in check (multiple relevant chunks are send to the LLM).

``chunk_overlap`` - Sets how much overlap there is between adjacent chunks. Overlap is useful to not miss any information that is potentially on the edge of a chunk or spread over multiple chunks. The trade-off is some redudancy in the database and increased computation.


Embedding
==================
**Key** ``embedding``

``provider`` - The provider of the embedding, for example OpenAI.

``model`` - The name of the model, as defined by the provider. Check the provider's API documentation for details. For OpenAI models make sure you have the environment variable ``OPENAI_API_KEY`` set, for AzureOpenAI ``AZURE_OPENAI_API_KEY``.


LLM
==============
**Key** ``llm``

``provider`` - The provider of the large language model, for example OpenAI.

``model`` - The name of the model, as defined by the provider. Check the provider's API documentation for details. For OpenAI models make sure you have the environment variable ``OPENAI_API_KEY`` set, for AzureOpenAI ``AZURE_OPENAI_API_KEY``.


For the llm type Azure OpenAI, the following additional keys must be provided.

``endpoint`` - The endpoint where the Azure model is hosted.

``api_version`` - The version of the API for the Azure model.
