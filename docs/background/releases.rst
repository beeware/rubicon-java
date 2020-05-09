===============
Release History
===============

.. towncrier release notes start

0.2.0
-----

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
