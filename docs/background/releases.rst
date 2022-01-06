===============
Release History
===============

.. towncrier release notes start

0.2.6 (2022-01-06)
==================

Features
--------

* Added support for arrays in arguments and return values. (#55)
* Added the ability to cast Java objects from one class to another. (#58)
* Local JNI Instances can be converted into global JNI instances using ``__global__()`` (#59)
* Added support for Python 3.9 and 3.10. (#62, #66)
* Methods that accept a Java ``NULL`` as an argument are now supported. (#63)
* Methods that return ``NULL`` now return typed ``NULL`` objects. (#67)

0.2.5 (2021-01-05)
==================

Features
--------

* Added support for passing Python lists into Java numeric array types (#53)


0.2.4 (2020-08-06)
==================

Features
--------

* Added support for implementing Java interfaces that return ``bool``. (#52)


0.2.3 (2020-07-27)
==================

Bugfixes
--------

* The asyncio event loop can now start on Python 3.6. (#51)


0.2.2 (2020-07-03)
==================

Features
--------

* Python's AsyncIO event loop is now integrated with the Android event loop.
  (#40, #49)
* ``sys.stdout`` & ``sys.stderr`` are now routed to the Android debug log using
  an ``android`` Python module. (#44)

Misc
----

* #45, #46, #47, #48


0.2.1 (2020-06-17)
==================

Features
--------

* Add the ability to implement Java interface methods that return `int`. (#42)

Misc
----

* #31, #37


0.2.1 (2020-06-17)
==================

Features
--------

* Add the ability to implement Java interface methods that return `int`. (#42)

Misc
----

* #31, #37


0.2.0
=====

Changes since v0.1.0:

- Port to Python 3, removing Python 2 support.
- Add support to Linux, allowing it to run on both macOS and Linux.
- Enable cross-compiling by adding support in the ``Makefile`` for specifying the compiler to use, the Python version whose headers to use, and to not require executing Python code during the build process.
- Adjust ``Python.run()`` to take a module name, not a filename.
- Add more documentation, although some is skeletal. Improvements to this are welcome.
- Add towncrier_ support. Future releases will rely on towncrier for release notes.
- Rename ``pybee`` to ``beeware``.
- Add GitHub Actions configuration for testing on macOS & Linux and Python 3.5, 3.6, 3.7, and 3.8.
- Support the ``JAVA_HOME`` environment variable to choose a Java compiler.

This version specifically targets Java 8 to simplify Android support.

Thanks to the contributors, listed by GitHub username in alphabetical order:

- @freakboy3742
- @glasnt
- @jacebrowning
- @paulproteus
- @RomanKharin

.. _towncrier: https://pypi.org/project/towncrier/
