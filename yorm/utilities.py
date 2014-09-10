"""Functions and decorators."""

import os


def store(dirpath, name=None, **kwargs):
    """Create a class decorator for YAML serialization."""
    if name is None:
        return dirpath

    def decorator(cls):

        class Decorated(cls):

            def __init__(self, *_args, **_kwargs):
                super().__init__(*_args, **_kwargs)
                base = os.path.join(dirpath.format(**kwargs), name)
                self.__path__ = base + '.yml'

        return Decorated

    return decorator


store_instances = store


def map_attribute(**kwargs):
    """Create a class decorator to mark attributes for serialization."""
    def _decorator(cls):
        return cls

    return _decorator
