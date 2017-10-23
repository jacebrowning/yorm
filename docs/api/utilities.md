# Utility Functions

YORM provides a set of utility functions to interact with mapped classes and instances in a manner similar to other ORMs.

**Create**

To create a new mapped object:

```python
yorm.create(MyClass, *my_args, **my_kwargs)
```

If YORM is allow to overwrite an existing file during the mapping:

```python
yorm.create(MyClass, ..., overwrite=True)
```

**Find**

> Documentation coming soon...

**Match**

To yield all matching instances of a mapped class:

```python
yorm.match(MyClass, **my_kwargs)
```

where `**my_kwargs` are zero or more keyword arguments to filter instances by.

**Load**

> Documentation coming soon...

**Save**

> Documentation coming soon...

**Delete**

> Documentation coming soon...

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
