"""Functions and decorators."""


def yormalize(dirpath, name=None, **kwargs):
    """Create a class decorator for YAML serialization."""
    if name is None:
        return dirpath

    def _decorator(cls):
        return cls

    return _decorator


def yattr(**kwargs):

    def _decorator(cls):
        return cls

    return _decorator

