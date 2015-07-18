"""Base classes for mapping."""

import abc
import functools

from .. import common
from ..mapper import MAPPER, get_mapper


log = common.logger(__name__)


def fetch_before(method):
    """Decorator for methods that should fetch before call."""
    @functools.wraps(method)
    def fetch_before(self, *args, **kwargs):  # pylint: disable=W0621
        """Decorated method."""
        mapper = get_mapper(self)
        if mapper and mapper.modified:
            log.debug("fetch before call: %s", method.__name__)
            mapper.fetch()
            if mapper.auto_store:
                mapper.store()
                mapper.modified = False
        return method(self, *args, **kwargs)
    return fetch_before


def store_after(method):
    """Decorator for methods that should store after call."""
    @functools.wraps(method)
    def store_after(self, *args, **kwargs):  # pylint: disable=W0621
        """Decorated method."""
        result = method(self, *args, **kwargs)
        mapper = get_mapper(self)
        if mapper and mapper.auto:
            log.debug("store after call: %s", method.__name__)
            mapper.store()
        return result
    return store_after


class Mappable(metaclass=abc.ABCMeta):  # pylint: disable=R0201

    """Base class for objects with attributes mapped to file."""

    def __getattribute__(self, name):
        """Trigger object update when reading attributes."""
        # TODO: remove MAPPER once renamed to '__mapper__'
        if name.startswith('__') or name == MAPPER:
            # avoid infinite recursion (attribute requested in this function)
            return object.__getattribute__(self, name)

        mapper = get_mapper(self)

        # Get the attribute's current value
        try:
            value = object.__getattribute__(self, name)
        except AttributeError as exc:
            missing = True
            if not mapper:
                raise exc from None
        else:
            missing = False

        # Fetch a new value from disk if the attribute is mapped or missing
        if mapper and (missing or (name in mapper.attrs and mapper.modified)):
            mapper.fetch()
            value = object.__getattribute__(self, name)

            # Store back to disk if this has been done before
            if mapper.auto_store:
                mapper.store()
                mapper.modified = False

        return value

    def __setattr__(self, name, value):
        """Trigger file update when setting attributes."""
        super().__setattr__(name, value)
        if name.startswith('__'):
            return

        mapper = get_mapper(self)
        if mapper and mapper.auto and name in mapper.attrs:
            mapper.store()

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
