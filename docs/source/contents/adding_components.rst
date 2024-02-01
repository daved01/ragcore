.. _adding_components:


*****************
Adding components
*****************

This section outlines the structure of ``ragcore`` and provides guidance on how you can add components. For detailed information about existing methods, refer to :ref:`api_reference`.

Supported model provider
=========================

The app supports OpenAI and Azure OpenAI for large language models and embedding models. For the former, a valid API key has to be in the environment with the name ``OPENAI_API_KEY``. For Azure deployments, the environment variable ``AZURE_OPENAI_API_KEY`` is required.


Adding a large language model
=============================

To add a new LLM, subclass the ``LLModel`` in ``models/llm_model.py`` and return the model in the ``_get_llm()`` method. This model is then used by the ``LLMService`` in ``services/llm_service.py``.



Adding an embedding
===================

To create a vector out of the input data so that it can be stored in the vector database, an OpenAI embedding model is used by default in the ``DatabaseService``. To change the embedding, subclass the ``EmbeddingModel`` in ``models/embedding_model.py``.

The default `OpenAI embedding <https://openai.com/blog/new-and-improved-embedding-model>`_ is ``text-embedding-ada-002``.


Adding new database
===================

To add a new vector database, subclass the ``VectorDataBaseModel`` and use it in the ``DatabaseService``. To learn more about what a vector database is and how it works, check out for example `this <https://www.pinecone.io/learn/vector-database/>`_ great post by the Pinecone team.


Changing prompt
==================

Using the retrieved information from the vector database, the information is concatenated to a string and along with the question passed into the ``PromptGenerator`` in ``models/prompt_model.py``. This prompt can be changed and it might be worth to experiment with variations.


Further changes
==================

The changes described so far swap out existing components. Further optimization could for example include changing the similarity measure used to retrieve vectors from the database, or using a different text splitting method in ``TextSplitterService`` in ``services/text_splitter_service.py`` (currently langchain's ``RecursiveCharacterTextSplitter`` is used).