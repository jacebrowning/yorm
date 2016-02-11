"""Base classes for mapping."""

import abc
import functools

from .. import common
from ..mapper import get_mapper


log = common.logger(__name__)


def fetch_before(method):
    """Decorator for methods that should fetch before call."""

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        """Decorated method."""
        if not _private_name(args):
            mapper = get_mapper(self)
            if mapper and mapper.modified:
                log.debug("Fetching before call: %s", method.__name__)
                mapper.fetch()
                if mapper.auto_store:
                    mapper.store()
                    mapper.modified = False

        return method(self, *args, **kwargs)

    return wrapped


def store_after(method):
    """Decorator for methods that should store after call."""

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        """Decorated method."""
        result = method(self, *args, **kwargs)

        if not _private_name(args):
            mapper = get_mapper(self)
            if mapper and mapper.auto:
                log.debug("Storing after call: %s", method.__name__)
                mapper.store()

        return result

    return wrapped


def _private_name(args, prefix='_'):
    """Determine if a call's first argument is a private variable name."""
    try:
        return args[0].startswith(prefix)
    except (IndexError, AttributeError):
        return False


class Mappable(metaclass=abc.ABCMeta):
    """Base class for objects with attributes mapped to file."""

    # pylint: disable=no-member

    @fetch_before
    def __getattribute__(self, name):
        """Trigger object update when reading attributes."""
        return object.__getattribute__(self, name)

    @store_after
    def __setattr__(self, name, value):
        """Trigger file update when setting attributes."""
        super().__setattr__(name, value)

    @fetch_before
    def __iter__(self):
        """Trigger object update when iterating."""
        return super().__iter__()

    @fetch_before
    def __getitem__(self, key):
        """Trigger object update when reading an index."""
        return super().__getitem__(key)

    @store_after
    def __setitem__(self, key, value):
        """Trigger file update when setting an index."""
        super().__setitem__(key, value)

    @store_after
    def __delitem__(self, key):
        """Trigger file update when deleting an index."""
        super().__delitem__(key)

    @store_after
    def append(self, value):
        """Trigger file update when appending items."""
        super().append(value)
