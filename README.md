YORM
====

[![Build Status](http://img.shields.io/travis/jacebrowning/yorm/master.svg)](https://travis-ci.org/jacebrowning/yorm)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/yorm/master.svg)](https://coveralls.io/r/jacebrowning/yorm)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/yorm.svg)](https://scrutinizer-ci.com/g/jacebrowning/yorm/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/yorm.svg)](https://pypi.python.org/pypi/yorm)
[![PyPI Downloads](http://img.shields.io/pypi/dm/yorm.svg)](https://pypi.python.org/pypi/yorm)

YORM provides functions and decorators to enable automatic, bidirectional, and human-friendly mappings of Python object attributes to YAML files.



Getting Started
===============

Requirements
------------

* Python 3.3+


Installation
------------

YORM can be installed with 'pip':

    $ pip install YORM

Or directly from the source code:

    $ git clone https://github.com/jacebrowning/yorm.git
    $ cd yorm
    $ python setup.py install



Basic Usage
===========

After installation, YORM imported from the package:

    $ python
    >>> import yorm
    yorm.__version__

YORM doesn't do anything yet.



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

    $ make env

Run the tests:

    $ make test
    $ make tests  # includes integration tests

Build the documentation:

    $ make doc

Run static analysis:

    $ make pep8
    $ make pep257
    $ make pylint
    $ make check  # includes all checks

Prepare a release:

    $ make dist  # dry run
    $ make upload
