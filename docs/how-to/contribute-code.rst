============================
Contributing code to Rubicon
============================

If you experience problems with Rubicon Java, `log them on GitHub`_. If you
want to contribute code, please `fork the code`_ and `submit a pull request`_.

.. _log them on Github: https://github.com/beeware/rubicon-java/issues
.. _fork the code: https://github.com/beeware/rubicon-java
.. _submit a pull request: https://github.com/beeware/rubicon-java/pulls

Setting up your development environment
---------------------------------------

The recommended way of setting up your development environment for Rubicon is
to use a `virtual environment <https://docs.python.org/3/library/venv.html>`__,
install the required dependencies and start coding:

.. tabs::

  .. group-tab:: macOS

    .. code-block:: bash

      $ git clone https://github.com/beeware/rubicon-java.git
      $ cd rubicon-java
      $ python3 -m venv venv
      $ . venv/bin/activate

  .. group-tab:: Linux

    .. code-block:: bash

      $ git clone https://github.com/beeware/rubicon-java.git
      $ cd rubicon-java
      $ python3 -m venv venv
      $ . venv/bin/activate

  .. group-tab:: Windows

    .. code-block:: doscon

      C:\...>git clone https://github.com/beeware/rubicon-java.git
      C:\...>cd rubicon-java
      C:\...>py -m venv venv
      C:\...>venv\Scripts\activate

To install all the development version of Rubicon, along with all it's
requirements, run the following commands within your virtual environment:

.. tabs::

  .. group-tab:: macOS

    .. code-block:: bash

      $ (venv) pip install -e .

  .. group-tab:: Linux

    .. code-block:: bash

      $ (venv) pip install -e .

  .. group-tab:: Windows

    .. code-block:: doscon

      C:\...>pip install -e .

Now you are ready to start hacking! Have fun!

To run the test suite, install PyTest, and run the test suite.

.. tabs::

  .. group-tab:: macOS

    .. code-block:: bash

      $ (venv) python setup.py test

  .. group-tab:: Linux

    .. code-block:: bash

      $ (venv) python setup.py test

  .. group-tab:: Windows

    .. code-block:: doscon

      C:\...>py setup.py test
