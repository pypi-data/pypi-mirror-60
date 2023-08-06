===============================
datemore
===============================

.. image:: https://travis-ci.com/romnnn/datemore.svg?branch=master
        :target: https://travis-ci.com/romnnn/datemore
        :alt: Build Status

.. image:: https://img.shields.io/pypi/v/datemore.svg
        :target: https://pypi.python.org/pypi/datemore
        :alt: PyPI version

.. image:: https://img.shields.io/github/license/romnnn/datemore
        :target: https://github.com/romnnn/datemore
        :alt: License

.. image:: https://readthedocs.org/projects/datemore/badge/?version=latest
        :target: https://datemore.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://codecov.io/gh/romnnn/datemore/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/romnnn/datemore
        :alt: Test Coverage

""""""""

Your short description here. `romnnn.github.io/datemore <https://romnnn.github.io/datemore>`_

.. code-block:: console

    $ pip install datemore

See the `official documentation`_ for more information.

.. _official documentation: https://datemore.readthedocs.io

.. code-block:: python

    import datemore

Development
-----------

For detailed instructions see `CONTRIBUTING <CONTRIBUTING.rst>`_.

Tests
~~~~~~~
You can run tests with

.. code-block:: console

    $ invoke test
    $ invoke test --min-coverage=90     # Fail when code coverage is below 90%
    $ invoke type-check                 # Run mypy type checks

Linting and formatting
~~~~~~~~~~~~~~~~~~~~~~~~
Lint and format the code with

.. code-block:: console

    $ invoke format
    $ invoke lint

All of this happens when you run ``invoke pre-commit``.

Note
-----

This project is still in the alpha stage and should not be considered production ready.
