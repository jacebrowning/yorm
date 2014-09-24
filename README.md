YORM
====

[![Build Status](http://img.shields.io/travis/jacebrowning/yorm/master.svg)](https://travis-ci.org/jacebrowning/yorm)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/yorm/master.svg)](https://coveralls.io/r/jacebrowning/yorm)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/yorm.svg)](https://scrutinizer-ci.com/g/jacebrowning/yorm/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/yorm.svg)](https://pypi.python.org/pypi/yorm)
[![PyPI Downloads](http://img.shields.io/pypi/dm/yorm.svg)](https://pypi.python.org/pypi/yorm)

YORM provides functions and decorators to enable automatic, bidirectional, and human-friendly mappings of Python object attributes to YAML files.

Uses beyond pure object serialization and object mapping include:

* automatic bidirectional conversion of attributes types
* attribute creation and type inference for new attributes
* storage of content in text files optimized for version control
* custom converters to map complex classes to JSON-compatible types


Getting Started
===============

Requirements
------------

* Python 3.3+

Installation
------------

YORM can be installed with pip:

    $ pip install YORM

Or directly from the source code:

    $ git clone https://github.com/jacebrowning/yorm.git
    $ cd yorm
    $ python setup.py install

Basic Usage
===========

Simply take an existing class:

```python

class Student:

    def __init__(name, number, grade=9):
        self.name = name
        self.number = number
        self.grade = grade
        self.gpa = 0.0
```

Define an attribute mapping:

```python

from yorm import store_instances, map_attr
from yorm.standard import 

@map_attr(name=String, grade=Integer, gpa=Float)
@store_instances("students/{self.grade}/{self.number}.yml")
class Student: ...
```

And interact with objects normally:

```python
>>> s1 = Student("John Doe", 123)
>>> s2 = Student("Jane Doe", 456, grade=12)
>>> s1.gpa = 3
```

Mapped attributes are automatically reflected on the filesytem:

```bash
$ cat students/9/123.yml
name: John Doe
gpa: 3.0
grade: 9
```

And in the objects:

```bash
$ echo "name: John Doe
> gpa: 1.8
> grade: 9
> expelled: true
" > students/9/123.yml
```

```python
>>> s1.gpa
1.8
>>> s1.expelled
True
```

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
