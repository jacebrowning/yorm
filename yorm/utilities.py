"""Functions and decorators."""

import os


def yormalize(dirpath, name=None, **kwargs):
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


def yattr(**kwargs):

    def _decorator(cls):
        return cls

    return _decorator

