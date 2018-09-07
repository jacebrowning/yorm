This documentation is a work in progress. Please help expand it.

---

# Containers

YORM has two container types:

```python
from yorm.types import List, Dictionary
```

## List

The `List` converter stores an attribute containing a sequence of homogenous values and is fetched as a `list`. The base class must extended for use and specify a single mapped attribute named `all`.

For example:

```python
@yorm.attr(all=Float)
class Things(List):
  ...

@yorm.attr(things=Things)
class Stuff:
  ...
```

will store the `things` attribute as a list of `float` values:

```yaml
things:
- 1.0
- 2.3
```

A shorthand syntax is also available to extend the `List` converter:

```python
List.of_type(<class>)
```

This is equivalent to the previous example:

```
@yorm.attr(things=List.of_type(Float))
class Stuff:
    ...
```

## Dictionary

TBD
