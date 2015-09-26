"""Functions and decorators."""

import uuid

from . import common, exceptions
from .bases import Mappable
from .mapper import get_mapper, set_mapper

log = common.logger(__name__)

UUID = 'UUID'


def sync(*args, **kwargs):
    """Convenience function to forward calls based on arguments.

    This function will call either:

    * `sync_object` - when given an unmapped object
    * `sync_instances` - when used as the class decorator

    Consult the signature of each call for more information.

    """
    if 'path_format' in kwargs or args and isinstance(args[0], str):
        return sync_instances(*args, **kwargs)
    else:
        return sync_object(*args, **kwargs)


def sync_object(instance, path, attrs=None, existing=None, auto=True):
    """Enable YAML mapping on an object.

    :param instance: object to patch with YAML mapping behavior
    :param path: file path for dump/load
    :param attrs: dictionary of attribute names mapped to converter classes
    :param existing: indicate if file is expected to exist or not
    :param auto: automatically store attributes to file

    """
    log.info("mapping %r to %s...", instance, path)
    _check_base(instance, mappable=False)

    attrs = attrs or common.attrs[instance.__class__]

    class Mapped(Mappable, instance.__class__):

        """Original class with `Mappable` as the base."""

    instance.__class__ = Mapped

    mapper = set_mapper(instance, path, attrs, auto=auto)
    _check_existance(mapper, existing)

    if mapper.auto:
        if not mapper.exists:
            mapper.create()
            mapper.store()
        mapper.fetch()

    log.info("mapped %r to '%s'", instance, path)
    return instance


def sync_instances(path_format, format_spec=None, attrs=None, **kwargs):
    """Class decorator to enable YAML mapping after instantiation.

    :param path_format: formatting string to create file paths for dump/load
    :param format_spec: dictionary to use for string formatting
    :param attrs: dictionary of attribute names mapped to converter classes
    :param existing: indicate if file is expected to exist or not
    :param auto: automatically store attribute to file

    """
    format_spec = format_spec or {}
    attrs = attrs or {}

    def decorator(cls):
        """Class decorator to map instances to files.."""

        old_init = cls.__init__

        def new_init(self, *_args, **_kwargs):
            """Modified class __init__ that maps the resulting instance."""
            old_init(self, *_args, **_kwargs)

            log.info("mapping instance of %r to '%s'...", cls, path_format)

            format_values = {}
            for key, value in format_spec.items():
                format_values[key] = getattr(self, value)
            if '{' + UUID + '}' in path_format:
                format_values[UUID] = uuid.uuid4().hex
            format_values['self'] = self

            path = path_format.format(**format_values)
            attrs.update(common.attrs[self.__class__])
            attrs.update(common.attrs[cls])

            sync_object(self, path, attrs, **kwargs)

        new_init.__doc__ = old_init.__doc__
        cls.__init__ = new_init

        return cls

    return decorator


def attr(**kwargs):
    """Class decorator to map attributes to converters.

    :param kwargs: keyword arguments mapping attribute name to converter class

    """
    def decorator(cls):
        """Class decorator."""
        for name, converter in kwargs.items():
            common.attrs[cls][name] = converter

        return cls

    return decorator


def update(instance, fetch=True, force=True, store=True):
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


def update_object(instance, existing=True, force=True):
    """Synchronize changes into a mapped object from its file.

    :param instance: object with patched YAML mapping behavior
    :param existing: indicate if file is expected to exist or not
    :param force: update the object even if the file appears unchanged

    """
    log.info("manually updating %r from file...", instance)
    _check_base(instance, mappable=True)

    mapper = get_mapper(instance)
    _check_existance(mapper, existing)

    if mapper.modified or force:
        mapper.fetch()


def update_file(instance, existing=None, force=True):
    """Synchronize changes into a mapped object's file.

    :param instance: object with patched YAML mapping behavior
    :param existing: indicate if file is expected to exist or not
    :param force: update the file even if automatic sync is off

    """
    log.info("manually saving %r to file...", instance)
    _check_base(instance, mappable=True)

    mapper = get_mapper(instance)
    _check_existance(mapper, existing)

    if mapper.auto or force:
        if not mapper.exists:
            mapper.create()
        mapper.store()


def _check_base(obj, mappable=True):
    """Confirm an object's base class is `Mappable` as required."""
    if mappable and not isinstance(obj, Mappable):
        raise exceptions.MappingError("{} is not mapped".format(repr(obj)))
    if not mappable and isinstance(obj, Mappable):
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
