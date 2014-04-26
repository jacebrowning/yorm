Yorm
====

[![Build Status](https://travis-ci.org/jacebrowning/yorm.png?branch=master)](https://travis-ci.org/jacebrowning/yorm)
[![Coverage Status](https://coveralls.io/repos/jacebrowning/yorm/badge.png?branch=master)](https://coveralls.io/r/jacebrowning/yorm?branch=master)
[![PyPI Version](https://badge.fury.io/py/Yorm.png)](http://badge.fury.io/py/Yorm)

Yorm is a TBD.



Getting Started
===============

Requirements
------------

* Python 3.3+


Installation
------------

Yorm can be installed with 'pip':

    pip install Yorm

Or directly from the source code:

    git clone https://github.com/jacebrowning/yorm.git
    cd yorm
    python setup.py install



Basic Usage
===========

After installation, Yorm imported from the package:

    python
    >>> import yorm
    yorm.__version__

Yorm doesn't do anything yet.



For Contributors
================

Requirements
------------

* GNU Make:
    * Windows: http://cygwin.com/install.html
    * Mac: https://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make (likely already installed)
* virtualenv: https://pypi.python.org/pypi/virtualenv#installation
* Pandoc: http://johnmacfarlane.net/pandoc/installing.html
* Graphviz: http://www.graphviz.org/Download.php


Installation
------------

Create a virtualenv:

    make env

Run the tests:

    make test
    make tests  # includes integration tests

Build the documentation:

    make doc

Run static analysis:

    make pep8
    make pylint
    make check  # pep8 and pylint

Prepare a release:

    make dist  # dry run
    make upload
