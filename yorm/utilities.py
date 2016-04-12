"""Functions to interact with mapped classes and instances."""

from . import common, exceptions

log = common.logger(__name__)


def update(instance, *, fetch=True, force=True, store=True):
    """Synchronize changes between a mapped object and its file.

    :param instance: object with patched YAML mapping behavior
    :param fetch: update the object with changes from its file
    :param force: even if the file appears unchanged
    :param store: update the file with changes from the object

    """
    _check_base(instance, mappable=True)

    if fetch:
        update_object(instance, force=False)
    if store:
        update_file(instance)
    if fetch:
        update_object(instance, force=force)


def update_object(instance, *, existing=True, force=True):
    """Synchronize changes into a mapped object from its file.

    :param instance: object with patched YAML mapping behavior
    :param existing: indicate if file is expected to exist or not
    :param force: update the object even if the file appears unchanged

    """
    log.info("Manually updating %r from file...", instance)
    _check_base(instance, mappable=True)

    mapper = common.get_mapper(instance)
    _check_existance(mapper, existing)

    if mapper.modified or force:
        mapper.fetch()


def update_file(instance, *, existing=None, force=True):
    """Synchronize changes into a mapped object's file.

    :param instance: object with patched YAML mapping behavior
    :param existing: indicate if file is expected to exist or not
    :param force: update the file even if automatic sync is off

    """
    log.info("Manually saving %r to file...", instance)
    _check_base(instance, mappable=True)

    mapper = common.get_mapper(instance)
    _check_existance(mapper, existing)

    if mapper.auto or force:
        if not mapper.exists:
            mapper.create()
        mapper.store()


def _synced(obj):
    """Determine if an object is already mapped to a file."""
    return bool(common.get_mapper(obj))


def _check_base(obj, mappable=True):
    """Confirm an object's base class is `Mappable` as required."""
    if mappable and not _synced(obj):
        raise exceptions.MappingError("{} is not mapped".format(repr(obj)))
    if not mappable and _synced(obj):
        raise exceptions.MappingError("{} is already mapped".format(repr(obj)))


def _check_existance(mapper, existing=None):
    """Confirm the expected state of the file.

    :param existing: indicate if file is expected to exist or not

    """
    if existing is True:
        if not mapper.exists:
            raise exceptions.FileMissingError
    elif existing is False:
        if mapper.exists:
            raise exceptions.FileAlreadyExistsError
