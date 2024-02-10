.. _api_reference:

****************
API reference
****************

Documentation of the different classes, starting from the app layer down to the model layer.

App
=======

.. automodule:: ragcore.app
    :members:

.. automodule:: ragcore.app.base_app
    :members:

Services
============

.. automodule:: ragcore.services.database_service
    :members:

.. automodule:: ragcore.services.document_service
    :members:

.. automodule:: ragcore.services.llm_service
    :members:

.. automodule:: ragcore.services.text_splitter_service
    :members:


Models
============

.. autoclass:: ragcore.models.database_model.BaseVectorDatabaseModel
    :members:

.. autoclass:: ragcore.models.database_model.BaseLocalVectorDatabaseModel
    :members:

.. autoclass:: ragcore.models.database_model.BaseRemoteVectorDatabaseModel
    :members:

.. autoclass:: ragcore.models.database_model.ChromaDatabase
    :members:

.. automodule:: ragcore.models.document_model
    :members:

.. automodule:: ragcore.models.app_model
    :members:
    
.. automodule:: ragcore.models.document_loader_model
    :members:


.. autoclass:: ragcore.models.embedding_model.BaseEmbedding
    :members:

.. autoclass:: ragcore.models.embedding_model.BaseOpenAIEmbeddings
    :members:

.. autoclass:: ragcore.models.embedding_model.AzureOpenAIEmbedding
    :members:

.. autoclass:: ragcore.models.embedding_model.OpenAIEmbedding
    :members:


.. autoclass:: ragcore.models.llm_model.BaseLLMModel
    :members:

.. autoclass:: ragcore.models.llm_model.AzureOpenAIModel
    :members:

.. autoclass:: ragcore.models.llm_model.OpenAIModel
    :members:


.. automodule:: ragcore.models.prompt_model
    :members:

Data Transfer Objects
======================

.. automodule:: ragcore.dto.document_dto
    :members:


Shared
============

.. automodule:: ragcore.shared.utils
    :members:


Constants
============

.. automodule:: ragcore.shared.constants
    :members:


Errors
============

.. automodule:: ragcore.shared.errors
    :members: