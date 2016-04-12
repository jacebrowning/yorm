"""Functions to interact with mapped classes and instances."""

from . import common, exceptions

log = common.logger(__name__)


def new(instance):
    """Create a new mapped object."""
    mapper = _ensure_mapped(instance)

    if mapper.exists:
        raise exceptions.FileAlreadyExistsError

    return save(instance)


def find(instance):
    """Find a matching mapped object or return None."""
    mapper = _ensure_mapped(instance)

    if mapper.exists:
        return instance
    else:
        return None


def load(cls, **kwargs):
    """Return a list of all matching mapped objects."""
    log.debug((cls, kwargs))
    raise NotImplementedError


def save(instance):
    """Save a mapped object to file."""
    mapper = _ensure_mapped(instance)

    if mapper.deleted:
        msg = "{!r} already deleted".format(instance)
        raise exceptions.FileDeletedError(msg)

    if not mapper.exists:
        mapper.create()

    mapper.store()

    return instance


def delete(instance):
    """Delete a mapped object's file."""
    mapper = _ensure_mapped(instance)

    mapper.delete()

    return None


def _ensure_mapped(obj, *, expected=True):
    mapper = common.get_mapper(obj)

    if mapper and not expected:
        msg = "{!r} is already mapped".format(obj)
        raise exceptions.MappingError(msg)

    if not mapper and expected:
        msg = "{!r} is not mapped".format(obj)
        raise exceptions.MappingError(msg)

    return mapper
