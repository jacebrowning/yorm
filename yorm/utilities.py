"""Functions to interact with mapped classes and instances."""

import inspect
import logging

from . import common, exceptions

log = logging.getLogger(__name__)


def create(class_or_instance, *args, overwrite=False, **kwargs):
    """Create a new mapped object.

    NOTE: Calling this function is unnecessary with 'auto_create' enabled.

    """
    instance = _instantiate(class_or_instance, *args, **kwargs)
    mapper = common.get_mapper(instance, expected=True)

    if mapper.exists and not overwrite:
        msg = "{!r} already exists".format(mapper.path)
        raise exceptions.DuplicateMappingError(msg)

    return load(save(instance))


def find(class_or_instance, *args, create=False, **kwargs):  # pylint: disable=redefined-outer-name
    """Find a matching mapped object or return None."""
    instance = _instantiate(class_or_instance, *args, **kwargs)
    mapper = common.get_mapper(instance, expected=True)

    if mapper.exists:
        return instance
    elif create:
        return save(instance)
    else:
        return None


def match(cls, **kwargs):
    """Yield all matching mapped objects."""
    log.debug((cls, kwargs))
    raise NotImplementedError


def load(instance):
    """Force the loading of a mapped object's file.

    NOTE: Calling this function is unnecessary. It exists for the
        aesthetic purpose of having symmetry between save and load.

    """
    mapper = common.get_mapper(instance, expected=True)

    mapper.load()

    return instance


def save(instance):
    """Save a mapped object to file.

    NOTE: Calling this function is unnecessary with 'auto_save' enabled.

    """
    mapper = common.get_mapper(instance, expected=True)

    if mapper.deleted:
        msg = "{!r} was deleted".format(mapper.path)
        raise exceptions.DeletedFileError(msg)

    if not mapper.exists:
        mapper.create()

    mapper.save()

    return instance


def delete(instance):
    """Delete a mapped object's file."""
    mapper = common.get_mapper(instance, expected=True)

    mapper.delete()

    return None


def _instantiate(class_or_instance, *args, **kwargs):
    if inspect.isclass(class_or_instance):
        instance = class_or_instance(*args, **kwargs)
    else:
        assert not args
        instance = class_or_instance

    return instance
