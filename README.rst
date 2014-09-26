Rubicon-Java
============

Rubicon-Java is a bridge between the Java Runtime Environment and Python.
It enables you to:

* Instantiate objects defined in Java
* Invoke methods on objects defined in Java
* Implement interfaces defined in Java

It also includes wrappers of the some key data types in the Java class library.

Quickstart
----------

To install Rubicon-Java, install it using pip:

    $ pip install rubicon-java

Then, in a Python shell:

    >>> from rubicon.java import JavaClass

    # Wrap a Java class
    >>> URL = JavaClass("java/net/URL")

    # Then instantiate the Java class, using the API
    # that is exposed in Java.
    >>> url = URL("http://pybee.org")

    # You can then call methods on the Java object as if it
    # were a Python object.
    >>> print url.getHost()
    pybee.org

Documentation
-------------

Full documentation for Rubicon can be found on `Read The Docs`_.

Community
---------

Rubicon is part of the `BeeWare suite`_. You can talk to the community through:

* `@pybeeware on Twitter`_

* The `BeeWare Users Mailing list`_, for questions about how to use the BeeWare suite.

* The `BeeWare Developers Mailing list`_, for discussing the development of new features in the BeeWare suite, and ideas for new tools for the suite.

Contributing
------------

If you experience problems with this backend, `log them on GitHub`_. If you
want to contribute code, please `fork the code`_ and `submit a pull request`_.

.. _BeeWare suite: http://pybee.org
.. _Read The Docs: http://rubicon-java.readthedocs.org
.. _@pybeeware on Twitter: https://twitter.com/pybeeware
.. _BeeWare Users Mailing list: https://groups.google.com/forum/#!forum/beeware-users
.. _BeeWare Developers Mailing list: https://groups.google.com/forum/#!forum/beeware-developers
.. _log them on Github: https://github.com/pybee/rubicon-java/issues
.. _fork the code: https://github.com/pybee/rubicon-java
.. _submit a pull request: https://github.com/pybee/rubicon-java/pulls
