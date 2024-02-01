.. _first_app:

********************************
Building your first application
********************************

Let's create an application with a local `Chroma <https://www.trychroma.com/>`_ database, the OpenAI LLM ``gpt-3.5-turbo``, and the OpenAI embedding model ``text-embedding-ada-002``.

Since we are using OpenAI components, we first have to set the OpenAI `API key <https://platform.openai.com/api-keys>`_ as described `here <https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key>`_. For example, in bash run

.. code-block:: bash

    export OPENAI_API_KEY=[your token]


Next, create a config file ``config.yaml`` in the root of your project with the following content:

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
      model: "text-embedding-ada-002"

    llm:
      provider: "openai"
      model: "gpt-3.5-turbo"


You can find more details and configuration options in the section :ref:`configuration`.

Next, create a Python file for the application code. Your project should look similar to this example now:

.. code-block:: bash

    myapp/
    ├── app.py
    ├── config.yaml

Finally, in the ``app.py`` file, we can implement our application using the components specified in the configuration. The following demonstrates the main methods:

.. code-block:: python

    from ragcore import RAGCore

    app = RAGCore() # pass config=<path-to-config.yaml> if not in root

    # Upload a document "My_Book.pdf"
    app.add(path="My_Book.pdf")

    # Now you can ask questions
    answer = app.query(query="What did the elk say?")

    print(answer)

    # You can delete by title
    app.delete(title="My_Book")

And that's it! For more details on configuration options, please refer to the :ref:`configuration` section.