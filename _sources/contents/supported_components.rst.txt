.. _supported_components:

**********************
Supported components
**********************

This section lists all available components and shows how to select them in the configuration file.
If you want to know what a specific component does and what role it plays in the system, take a look at :ref:`Architecture <about>`.
And if you don't find the component you are looking for, feel free to `add <https://github.com/daved01/ragcore>`_ it and open a pull request!


Readers
=================
Readers parse documents so that they can be added to the sytem's database. Currently supported is text in the following file formats:

- pdf


Splitters
=================
Splitters take the text during ingestion and split it into chunks.
Currently supported is a recursive text splitter only, so there is no option to select one in the configuration file yet.


Vector Databases
=================
The database stores your embeddings and (references to) your document chunks. RAG Core supports both local and remote databases.
The latter is a database which is hosted, for example, by a cloud provider.


Local Databases
-----------------

.. table:: Config key ``provider``

   +-----------------------------------------+--------------+--------------------------------------------------------+
   | Database                                | config value | requires                                               |
   +=========================================+==============+========================================================+
   | `Chroma <https://www.trychroma.com>`_   | ``"chroma"`` | ``base_dir`` in config                                 |
   +-----------------------------------------+--------------+--------------------------------------------------------+

Remote Databases
-----------------

.. table:: Config key ``provider``

   +-----------------------------------------+--------------+--------------------------------------------------------+
   | Database                                | config value | requires                                               |
   +=========================================+==============+========================================================+
   | `Pinecone <https://www.pinecone.io>`_   |``"pinecone"``| ``base_url`` in config,                                |
   |                                         |              | ``PINECONE_API_KEY`` environment variable              |
   +-----------------------------------------+--------------+--------------------------------------------------------+


Embeddings
=================
The embedding model is used to create a vector representation of your document chunks and queries.
Currently, the following remote embedding model families are supported.

.. table:: Config key ``provider``

   +---------------------------------------------------------------------------------------------------------------------------+--------------+--------------------------------------------------------+
   | Embedding model family                                                                                                    | config value | requires                                               |
   +===========================================================================================================================+==============+========================================================+
   | `OpenAI <https://platform.openai.com/docs/guides/embeddings>`_                                                            | ``"openai"`` | ``OPENAI_API_KEY`` environment variable                |
   +---------------------------------------------------------------------------------------------------------------------------+--------------+--------------------------------------------------------+
   | `Azure OpenAI <https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#embeddings-models>`_            | ``"azure"``  | ``AZURE_OPENAI_API_KEY`` environment variable          |
   +---------------------------------------------------------------------------------------------------------------------------+--------------+--------------------------------------------------------+



LLMs
=================
The Large Language Model generates a response in natural language using the retrieved chunks and a prompt.

.. table:: Config key ``provider``

   +-----------------------------------------------------------------------------------------------+--------------+--------------------------------------------------------+
   | LLM model family                                                                              | config value | requires                                               |
   +===============================================================================================+==============+========================================================+
   | `OpenAI <https://platform.openai.com/docs/guides/text-generation>`_                           | ``"openai"`` | ``OPENAI_API_KEY`` environment variable                |
   +-----------------------------------------------------------------------------------------------+--------------+--------------------------------------------------------+
   | `Azure OpenAI <https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models>`_  | ``"azure"``  | ``AZURE_OPENAI_API_KEY`` environment variable          |
   +-----------------------------------------------------------------------------------------------+--------------+--------------------------------------------------------+
