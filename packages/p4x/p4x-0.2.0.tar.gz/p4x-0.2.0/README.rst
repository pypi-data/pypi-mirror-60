========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-p4x/badge/?style=flat
    :target: https://readthedocs.org/projects/python-p4x
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/philipptempel/python-p4x.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/philipptempel/python-p4x

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/philipptempel/python-p4x?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/philipptempel/python-p4x

.. |requires| image:: https://requires.io/github/philipptempel/python-p4x/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/philipptempel/python-p4x/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/philipptempel/python-p4x/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/philipptempel/python-p4x

.. |version| image:: https://img.shields.io/pypi/v/p4x.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/p4x

.. |wheel| image:: https://img.shields.io/pypi/wheel/p4x.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/p4x

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/p4x.svg
    :alt: Supported versions
    :target: https://pypi.org/project/p4x

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/p4x.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/p4x

.. |commits-since| image:: https://img.shields.io/github/commits-since/philipptempel/python-p4x/v0.2.0.svg
    :alt: Commits since latest release
    :target: https://github.com/philipptempel/python-p4x/compare/v0.2.0...master



.. end-badges

Philipp Tempel's Personal Python Package. Includes lots of self-made modules and methods.

* Free software: MIT license

Installation
============

::

    pip install p4x

You can also install the in-development version with::

    pip install https://github.com/philipptempel/python-p4x/archive/master.zip


Documentation
=============


https://python-p4x.readthedocs.io/


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
