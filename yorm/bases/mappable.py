"""Base classes for mapping."""

import abc
import functools

from .. import common


log = common.logger(__name__)

TAG = '_modified_by_yorm'


def fetch_before(method):
    """Decorator for methods that should fetch before call."""

    if getattr(method, TAG, False):
        return method

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        """Decorated method."""
        if not _private_call(method, args):
            mapper = common.get_mapper(self)
            if mapper and mapper.modified:
                log.debug("Fetching before call: %s", method.__name__)
                mapper.fetch()
                if mapper.store_after_fetch:
                    mapper.store()
                    mapper.modified = False

        return method(self, *args, **kwargs)

    setattr(wrapped, TAG, True)

    return wrapped


def store_after(method):
    """Decorator for methods that should store after call."""

    if getattr(method, TAG, False):
        return method

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        """Decorated method."""
        result = method(self, *args, **kwargs)

        if not _private_call(method, args):
            mapper = common.get_mapper(self)
            if mapper and mapper.auto:
                log.debug("Storing after call: %s", method.__name__)
                mapper.store()

        return result

    setattr(wrapped, TAG, True)

    return wrapped


def _private_call(method, args, prefix='_'):
    """Determine if a call's first argument is a private variable name."""
    if method.__name__ in ('__getattribute__', '__setattr__'):
        assert isinstance(args[0], str)
        return args[0].startswith(prefix)
    else:
        return False


# TODO: move these methods inside of `Container`
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


def patch_methods(instance):
    log.debug("Patching methods on: %r", instance)
    cls = instance.__class__

    # TODO: determine a way to share the lists of methods to patch
    for name in ['__getattribute__', '__iter__', '__getitem__']:
        try:
            method = getattr(cls, name)
        except AttributeError:
            log.trace("No method: %s", name)
        else:
            modified_method = fetch_before(method)
            setattr(cls, name, modified_method)
            log.trace("Patched to fetch before call: %s", name)

    for name in ['__setattr__', '__setitem__', '__delitem__', 'append']:
        try:
            method = getattr(cls, name)
        except AttributeError:
            log.trace("No method: %s", name)
        else:
            modified_method = store_after(method)
            setattr(cls, name, modified_method)
            log.trace("Patched to store after call: %s", name)
