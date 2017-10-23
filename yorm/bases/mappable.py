"""Base classes for mapping."""

import abc
import functools
import logging

from .. import common

log = logging.getLogger(__name__)


def load_before(method):
    """Decorate methods that should load before call."""

    if getattr(method, '_load_before', False):
        return method

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = True  # pylint: disable=unused-variable

        if not _private_call(method, args):
            mapper = common.get_mapper(self)
            if mapper and mapper.modified:
                log.debug("Loading before call: %s", method.__name__)
                mapper.load()
                if mapper.auto_save_after_load:
                    mapper.save()
                    mapper.modified = False

        return method(self, *args, **kwargs)

    setattr(wrapped, '_load_before', True)

    return wrapped


def save_after(method):
    """Decorate methods that should save after call."""

    if getattr(method, '_save_after', False):
        return method

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = True  # pylint: disable=unused-variable

        result = method(self, *args, **kwargs)

        if not _private_call(method, args):
            mapper = common.get_mapper(self)
            if mapper and mapper.auto_save:
                log.debug("Saving after call: %s", method.__name__)
                mapper.save()

        return result

    setattr(wrapped, '_save_after', True)

    return wrapped


def _private_call(method, args, prefix='_'):
    """Determine if a call's first argument is a private variable name."""
    if method.__name__ in ('__getattribute__', '__setattr__'):
        assert isinstance(args[0], str)
        return args[0].startswith(prefix)
    else:
        return False


class Mappable(metaclass=abc.ABCMeta):
    """Base class for objects with attributes mapped to file."""

    # pylint: disable=no-member

    @load_before
    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    @save_after
    def __setattr__(self, name, value):
        super().__setattr__(name, value)

    @load_before
    def __iter__(self):
        return super().__iter__()

    @load_before
    def __getitem__(self, key):
        return super().__getitem__(key)

    @save_after
    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    @save_after
    def __delitem__(self, key):
        super().__delitem__(key)

    @save_after
    def append(self, *args, **kwargs):
        super().append(*args, **kwargs)

    @save_after
    def extend(self, *args, **kwargs):
        super().extend(*args, **kwargs)

    @save_after
    def insert(self, *args, **kwargs):
        super().insert(*args, **kwargs)

    @save_after
    def remove(self, *args, **kwargs):
        super().remove(*args, **kwargs)

    @save_after
    def pop(self, *args, **kwargs):
        super().pop(*args, **kwargs)

    @save_after
    def clear(self, *args, **kwargs):
        super().clear(*args, **kwargs)

    @save_after
    def sort(self, *args, **kwargs):
        super().sort(*args, **kwargs)

    @save_after
    def reverse(self, *args, **kwargs):
        super().reverse(*args, **kwargs)

    @save_after
    def popitem(self, *args, **kwargs):
        super().popitem(*args, **kwargs)

    @save_after
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)


_LOAD_BEFORE_METHODS = [
    '__getattribute__',
    '__iter__',
    '__getitem__',
]
_SAVE_AFTER_METHODS = [
    '__setattr__',
    '__setitem__',
    '__delitem__',
    'append',
    'extend',
    'insert',
    'remove',
    'pop',
    'clear',
    'sort',
    'reverse',
    'popitem',
    'update',
]


def patch_methods(instance):
    log.debug("Patching methods on: %r", instance)
    cls = instance.__class__

    for name in _LOAD_BEFORE_METHODS:
        try:
            method = getattr(cls, name)
        except AttributeError:
            log.trace("No method: %s", name)
        else:
            modified_method = load_before(method)
            setattr(cls, name, modified_method)
            log.trace("Patched to load before call: %s", name)

    for name in _SAVE_AFTER_METHODS:
        try:
            method = getattr(cls, name)
        except AttributeError:
            log.trace("No method: %s", name)
        else:
            modified_method = save_after(method)
            setattr(cls, name, modified_method)
            log.trace("Patched to save after call: %s", name)
