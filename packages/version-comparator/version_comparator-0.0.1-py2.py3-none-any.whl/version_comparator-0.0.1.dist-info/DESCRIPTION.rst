========
Overview
========



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


Changelog
=========

0.0.1 (2020-01-29)
------------------

* First release on PyPI.


