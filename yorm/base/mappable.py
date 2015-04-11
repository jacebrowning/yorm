"""Base class for mapped objects."""

import abc
import functools

from .. import common

log = common.logger(__name__)


MAPPER = 'yorm_mapper'


def fetch_before(method):
    """Decorator for methods that should fetch before call."""
    @functools.wraps(method)
    def decorated_method(self, *args, **kwargs):
        """Decorated method."""
        mapper = getattr(self, MAPPER)
        mapper.fetch()
        return method(self, *args, **kwargs)
    return decorated_method


def store_after(method):
    """Decorator for methods that should store after call."""
    @functools.wraps(method)
    def decorated_method(self, *args, **kwargs):
        """Decorated method."""
        result = method(self, *args, **kwargs)
        mapper = getattr(self, MAPPER, None)
        if mapper and mapper.auto:
            mapper.store()
        return result
    return decorated_method


class Mappable(metaclass=abc.ABCMeta):  # pylint: disable=R0201

    """Base class for objects with attributes mapped to file."""

    def __getattribute__(self, name):
        """Trigger object update when reading attributes."""
        if name in ('__dict__', MAPPER):
            # avoid infinite recursion (attribute requested in this function)
            return object.__getattribute__(self, name)
        mapper = getattr(self, MAPPER, None)

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
        if mapper and (missing or name in mapper.attrs):
            mapper.fetch()
            value = object.__getattribute__(self, name)

        return value

    def __setattr__(self, name, value):
        """Trigger file update when setting attributes."""
        super().__setattr__(name, value)

        mapper = getattr(self, MAPPER, None)
        if mapper and mapper.auto and name in mapper.attrs:
            self.yorm_mapper.store()

    @fetch_before
    def __getitem__(self, key):
        """Trigger object update when reading an index."""
        return super().__getitem__(key)

    @store_after
    def __setitem__(self, key, value):
        """Trigger file update when setting an index."""
        super().__setitem__(key, value)

    @store_after
    def append(self, value):
        """Trigger file update when appending items."""
        super().append(value)
