.. image:: https://beeware.org/project/projects/bridges/rubicon/rubicon.png
    :width: 72px
    :target: https://beeware.org/rubicon

Rubicon-Java
============

.. image:: https://img.shields.io/pypi/pyversions/rubicon-java.svg
   :target: https://pypi.python.org/pypi/rubicon-java
   :alt: Python Versions

.. image:: https://img.shields.io/pypi/v/rubicon-java.svg
   :target: https://pypi.python.org/pypi/rubicon-java
   :alt: Project version

.. image:: https://img.shields.io/pypi/status/rubicon-java.svg
   :target: https://pypi.python.org/pypi/rubicon-java
   :alt: Project status

.. image:: https://img.shields.io/pypi/l/rubicon-java.svg
   :target: https://github.com/beeware/rubicon-java/blob/master/LICENSE
   :alt: License

.. image:: https://github.com/beeware/rubicon-java/workflows/CI/badge.svg?branch=master
   :target: https://github.com/beeware/rubicon-java/actions
   :alt: Build Status

.. image:: https://img.shields.io/discord/836455665257021440?label=Discord%20Chat&logo=discord&style=plastic
   :target: https://beeware.org/bee/chat/
   :alt: Discord server

Rubicon-Java is a bridge between the Java Runtime Environment and Python.
It enables you to:

* Instantiate objects defined in Java,
* Invoke static and instance methods on objects defined in Java,
* Access and modify static and instance fields on objects defined in Java, and
* Write and use Python implementations of interfaces defined in Java.

Quickstart
----------

Rubicon-Java consists of three components:

1. A Python library,
2. A JNI library, and
3. A Java JAR file.

A ``Makefile`` has been provided to compile the JNI and JAR components. Type::

    $ make

to compile them. The compiled output will be placed in the ``build`` directory.

To use Rubicon-Java, you'll need to ensure:

1. ``rubicon.jar`` is in the classpath when you start your Java VM.

2. The Rubicon library file is somewhere that it will be found by dynamic
   library discovery. This means:

   a. Under OS X, put the directory containing ``librubicon.dylib`` is in your ``DYLD_LIBRARY_PATH``

   b. Under Linux, put the directory containing ``librubicon.so`` is in your ``LD_LIBRARY_PATH``

   c. Under Windows.... something :-)

3. The ``rubicon`` Python module is somewhere that can be added to a
   ``PYTHONPATH``. You can install rubicon using::

       $ pip install rubicon-java

   If you do this, you'll need to reference your system Python install when
   setting your ``PYTHONPATH``.

The Rubicon bridge starts on the Java side. Import the Python object::

    import org.beeware.rubicon.Python;

Then start the Python interpreter, and run a Python file::

    # Initialize the Python VM
    String pythonHome = "/path/to/python";
    String pythonPath = "/path/to/dir1:/path/to/dir2";
    if (Python.start(pythonHome, pythonPath, null) != 0) {
        System.out.println("Error initializing Python VM.");
    }

    # Start a Python module
    if (Python.run("path.of.module") != 0) {
        System.out.println("Error running Python script.");
    }

    # Shut down the Python VM.
    Python.stop();

The ``PYTHONPATH`` you specify must enable access to the ``rubicon`` Python
module.

In your Python script, you can then reference Java objects::

    >>> from rubicon.java import JavaClass

    # Wrap a Java class
    >>> URL = JavaClass("java/net/URL")

    # Then instantiate the Java class, using the API
    # that is exposed in Java.
    >>> url = URL("https://beeware.org")

    # You can then call methods on the Java object as if it
    # were a Python object.
    >>> print(url.getHost())
    beeware.org

It's also possible to provide implementations of Java Interfaces in Python.
For example, lets say you want to create a Swing Button, and you want to
respond to button clicks::

    >>> from rubicon.java import JavaClass, JavaInterface

    # Wrap the Java interface
    >>> ActionListener = JavaInterface('java/awt/event/ActionListener')

    # Define your own implementation
    >>> class MyActionListener(ActionListener):
    ...     def actionPerformed(self, event):
    ...         print("Button Pressed")

    # Instantiate an instance of the listener
    >>> listener = MyActionListener()

    # Create a button, and set the listener
    >>> Button = JavaClass('javax/swing/JButton')
    >>> button = Button('Push it')
    >>> button.setActionListener(listener)

Of course, this sample code won't work unless it's in the context of a larger
application starting a Swing GUI and so on.

Testing
-------

To run the Rubicon test suite:

1. Ensure that ``java`` is on your ``$PATH``, or set the ``JAVA_HOME`` environment
   variable to point to a directory of a Java Development Kit (JDK).

2. Create a Python 3 virtual environment, and ensure that pip & setuptools are
   up to date::

    $ python3 -m venv venv
    $ source venv/bin/activate
    (venv) $ python -m pip install --upgrade pip
    (venv) $ python -m pip install --upgrade setuptools

3. Install ``tox``::

    (venv) $ python -m pip install tox

4. Run the test suite. The following should work properly on both macOS and
   Linux::

    (venv) $ tox -e py

This will compile the Rubicon library, compile the Java test classes, and
run the Python test suite from within the Java environment.

Documentation
-------------

Full documentation for Rubicon can be found on `Read The Docs`_.

Community
---------

Rubicon is part of the `BeeWare suite`_. You can talk to the community through:

* `@PyBeeWare on Twitter`_

* The `beeware/general`_ channel on Gitter.

We foster a welcoming and respectful community as described in our
`BeeWare Community Code of Conduct`_.

Contributing
------------

If you experience problems with this backend, `log them on GitHub`_. If you
want to contribute code, please `fork the code`_ and `submit a pull request`_.

.. _BeeWare suite: http://beeware.org
.. _Read The Docs: http://rubicon-java.readthedocs.org
.. _@PyBeeWare on Twitter: https://twitter.com/PyBeeWare
.. _beeware/general: https://gitter.im/beeware/general
.. _BeeWare Community Code of Conduct: http://beeware.org/community/behavior/
.. _log them on Github: https://github.com/beeware/rubicon-java/issues
.. _fork the code: https://github.com/beeware/rubicon-java
.. _submit a pull request: https://github.com/beeware/rubicon-java/pulls
