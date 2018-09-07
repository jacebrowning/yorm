[![Build Status](http://img.shields.io/travis/jacebrowning/yorm/master.svg)](https://travis-ci.org/jacebrowning/yorm)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/yorm/master.svg)](https://coveralls.io/r/jacebrowning/yorm)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/yorm.svg)](https://scrutinizer-ci.com/g/jacebrowning/yorm/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/yorm.svg)](https://pypi.python.org/pypi/yorm)

# Overview

YORM enables automatic, bidirectional, human-friendly mappings of object attributes to YAML files.
 Uses beyond typical object serialization and relational mapping include:

* bidirectional conversion between basic YAML and Python types
* attribute creation and type inference for new attributes
* storage of content in text files optimized for version control
* extensible converters to customize formatting on complex classes

View the talk from [PyOhio 2015](https://www.youtube.com/watch?v=0woNEKf-wAo).

## Requirements

* Python 3.5+

## Installation

Install YORM with pip:

```sh
$ pip install YORM
```

or directly from the source code:

```sh
$ git clone https://github.com/jacebrowning/yorm.git
$ cd yorm
$ python setup.py install
```

# Usage

Simply take an existing class:

```python
class Student:
    def __init__(self, name, school, number, year=2009):
        self.name = name
        self.school = school
        self.number = number
        self.year = year
        self.gpa = 0.0
```

and define an attribute mapping:

```python
import yorm
from yorm.types import String, Integer, Float

@yorm.attr(name=String, year=Integer, gpa=Float)
@yorm.sync("students/{self.school}/{self.number}.yml")
class Student:
    ...
```

Modifications to each object's mapped attributes:

```python
>>> s1 = Student("John Doe", "GVSU", 123)
>>> s2 = Student("Jane Doe", "GVSU", 456, year=2014)
>>> s1.gpa = 3
```

are automatically reflected on the filesytem:

```sh
$ cat students/GVSU/123.yml
name: John Doe
gpa: 3.0
school: GVSU
year: 2009
```

Modifications and new content in each mapped file:

```sh
$ echo "name: John Doe
> gpa: 1.8
> year: 2010
" > students/GVSU/123.yml
```

are automatically reflected in their corresponding object:

```python
>>> s1.gpa
1.8
```
