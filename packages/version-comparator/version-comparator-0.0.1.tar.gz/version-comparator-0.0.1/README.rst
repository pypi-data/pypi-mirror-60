========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |version| image:: https://img.shields.io/pypi/v/version-comparator.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/version-comparator

.. |wheel| image:: https://img.shields.io/pypi/wheel/version-comparator.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/version-comparator

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/version-comparator.svg
    :alt: Supported versions
    :target: https://pypi.org/project/version-comparator

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/version-comparator.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/version-comparator

.. |commits-since| image:: https://img.shields.io/github/commits-since/pcu4dros/pedro_cuadros_test/python-version-comparator/v0.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/pcu4dros/pedro_cuadros_test/python-version-comparator/compare/v0.0.1...master



.. end-badges

An example package. Checks if a version is equal to, greater or less than another version

* Free software: BSD 3-Clause License

Installation
============

::

    pip install version-comparator

You can also install the in-development version with::

    pip install https://github.com/pcu4dros/pedro_cuadros_test/python-version-comparator/archive/master.zip


Documentation
=============


Project
=======

The goal of this question is to write a software library that accepts 2 version string as input and
returns whether one is greater than, equal, or less than the other. As an example: “1.2” is
greater than “1.1”.

=====
Usage
=====

To use Distributed LRU Cache in a project::


	import compare_versions

        compare_versions('1.2.1', '1.2.1')


Where::

   0: The version are equal
   1: The version is greater then the other version
   -1: The version is less than the other version


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
