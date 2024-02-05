.. _develop:

*****************
Development setup
*****************

To begin development for the library, follow the instructions below to set up your environment.

**Preparing environment**

First, clone the repo and navigate to it

.. code-block:: bash

    git clone https://github.com/daved01/ragcore.git
    cd ragcore

Then, create and activate a virtual environment

.. code-block:: bash
    
    python -m venv venv


or with ``pyenv-virtualenv`` and for example Python ``3.11.3``

.. code-block:: bash
    
    pyenv virtualenv 3.11.3 venv
    pyenv activate venv

For more information on managing virtual environments with pyenv-virtualenv see `here <https://www.neuralception.com/pyenvvirtualenv/>`_.


**Installing dependencies**

Install ``ragcore`` in editable mode using

.. code-block:: bash
    
    pip install -e .

Then install the development requirements

.. code-block:: bash

    pip install -r requirements_dev.txt


**Validating installation**

Finally, to validate the installation you can run the tests

.. code-block:: bash

    pytest tests
