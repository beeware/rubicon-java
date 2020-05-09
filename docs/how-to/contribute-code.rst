=================================
How to contribute code to Rubicon
=================================

If you experience problems with Rubicon, `log them on GitHub`_. If you want
to contribute code, please `fork the code`_ and `submit a pull request`_.

.. _log them on Github: https://github.com/beeware/rubicon-java/issues
.. _fork the code: https://github.com/beeware/rubicon-java
.. _submit a pull request: https://github.com/beeware/rubicon-java/pulls

.. _setup-dev-environment:

Set up your development environment
===================================

The recommended way of setting up your development environment for Rubicon is
to install a virtual environment, install the required dependencies and start
coding:

.. code-block:: sh

    $ python3 -m venv venv
    $ source venv/bin/activate.sh
    (venv) $ python -m pip install --upgrade pip
    (venv) $ python -m pip install --upgrade setuptools
    (venv) $ git clone https://github.com/beeware/rubicon-java.git
    (venv) $ cd rubicon-objc
    (venv) $ python -m pip install -e .

Rubicon uses tox to describe it's testing environment. To install tox, run:

.. code-block:: sh

    (venv) $ python -m pip install tox

You can then run the full test suite:

.. code-block:: sh

    (venv) $ tox

By default this will run the test suite multiple times, once on each Python
version supported by Rubicon, as well as running some pre-commit checks of
code style and validity. This can take a while, so if you want to speed up
the process while developing, you can run the tests on one Python version only:

.. code-block:: sh

    (venv) $ tox -e py

Or, to run using a specific version of Python:

.. code-block:: sh

    (venv) $ tox -e py37

substituting the version number that you want to target. You can also specify
one of the pre-commit checks `flake8`, `docs` or `package` to check code
formatting, documentation syntax and packaging metadata, respectively.

Now you are ready to start hacking on Rubicon. Have fun!
