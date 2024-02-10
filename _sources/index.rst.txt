.. RAG Core Kit documentation master file, created by
   sphinx-quickstart on Sat Jan 27 20:22:08 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RAG Core documentation
========================================

RAG Core is a library designed to reduce the implementation of Retrieval-Augmented Generation applications to a configuration file and a few lines of code.

To get started, run 

.. code-block:: bash

   pip install ragcore

Once you have selected the components that suit your needs with the config file, creating a Retrieval-Augmented Generation system becomes as easy as this:

.. code-block:: python

   from ragcore import RAGCore

   app = RAGCore() # pass config=<path-to-config.yaml> if not in root

   # Upload a document "My_Book.pdf"
   app.add(path="My_Book.pdf")

   # Now you can ask questions
   answer = app.query(query="What did the elk say?")

   print(answer.content)

   # List the document's title and content on which the answer is based
   for doc in answer.documents:
      print(doc.title, " | ", doc.content)

   # You can delete by title
   app.delete(title="My_Book")


.. toctree::
   :maxdepth: 2
   :caption: About RAG
   
   contents/about

.. toctree::
   :maxdepth: 2
   :caption: Getting started
   
   contents/installation
   contents/first_app

.. toctree::
   :maxdepth: 2
   :caption: Usage guide
   
   contents/configuration
   contents/supported_components

.. toctree::
   :maxdepth: 2
   :caption: Developer guide
   
   contents/develop
   contents/adding_components
   contents/api_reference



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
