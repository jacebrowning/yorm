# Class Mapping

Instances of any class can be mapped to the file system. For these examples, a `Student` class will be used:

```python
class Student:
    def __init__(self, name, school, number, year=2009):
        self.name = name
        self.school = school
        self.number = number
        self.year = year
        self.gpa = 0.0
```

To map instances of this class to files, apply the `yorm.sync()` decorator to that class' definition:

```python
import yorm

@yorm.sync("students/{self.school}/{self.number}.yml")
class Student:
    ...
```

# Attribute Selection

To control which attributes should be included in the mapping, apply one or more `yorm.attr()` decorators specifying the attribute type:

```python
import yorm
from yorm.types import String, Integer, Float

@yorm.attr(name=String, year=Integer, gpa=Float)
@yorm.sync("students/{self.school}/{self.number}.yml")
class Student:
    ...
```

# ORM Methods

If you would like your class and its instances to behave more like a traditional object-relational mapping (ORM) model, use the provided mixin class:

```python
import yorm

class Student(yorm.ModelMixin):
    ...
```

which will add the following class methods:

- `new` - object factory
- `find` - return a single matching object
- `match` - return all matching objects

and instance methods:

- `load` - update the object from its file
- `save` - update the file from its object
- `delete` - delete the object's file

