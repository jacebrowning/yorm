"""Functions and decorators."""

import uuid
from collections import OrderedDict

from . import common, exceptions
from .bases.mappable import patch_methods
from .mapper import Mapper

log = common.logger(__name__)


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


def sync_object(instance, path, attrs=None, existing=None, **kwargs):
    """Enable YAML mapping on an object.

    :param instance: object to patch with YAML mapping behavior
    :param path: file path for dump/load
    :param attrs: dictionary of attribute names mapped to converter classes
    :param existing: indicate if file is expected to exist or not
    :param auto: automatically store attributes to file
    :param strict: ignore new attributes in files

    """
    log.info("Mapping %r to %s...", instance, path)
    _check_base(instance, mappable=False)

    patch_methods(instance)

    attrs = _ordered(attrs) or common.attrs[instance.__class__]
    mapper = Mapper(instance, path, attrs, **kwargs)
    common.set_mapper(instance, mapper)
    _check_existance(mapper, existing)

    if mapper.auto:
        if not mapper.exists:
            mapper.create()
            mapper.store()
        mapper.fetch()

    log.info("Mapped %r to %s", instance, path)
    return instance


def sync_instances(path_format, format_spec=None, attrs=None, **kwargs):
    """Class decorator to enable YAML mapping after instantiation.

    :param path_format: formatting string to create file paths for dump/load
    :param format_spec: dictionary to use for string formatting
    :param attrs: dictionary of attribute names mapped to converter classes
    :param existing: indicate if file is expected to exist or not
    :param auto: automatically store attributes to file

    """
    format_spec = format_spec or {}
    attrs = attrs or OrderedDict()

    def decorator(cls):
        """Class decorator to map instances to files.."""

        init = cls.__init__

        def modified_init(self, *_args, **_kwargs):
            """Modified class __init__ that maps the resulting instance."""
            init(self, *_args, **_kwargs)

            log.info("Mapping instance of %r to '%s'...", cls, path_format)

            format_values = {}
            for key, value in format_spec.items():
                format_values[key] = getattr(self, value)
            if '{' + common.UUID + '}' in path_format:
                format_values[common.UUID] = uuid.uuid4().hex
            format_values['self'] = self

            common.attrs[cls].update(attrs)
            common.attrs[cls].update(common.attrs[self.__class__])
            path = path_format.format(**format_values)
            sync_object(self, path, **kwargs)

        modified_init.__doc__ = init.__doc__
        cls.__init__ = modified_init

        return cls

    return decorator


def attr(**kwargs):
    """Class decorator to map attributes to types.

    :param kwargs: keyword arguments mapping attribute name to converter class

    """
    if len(kwargs) != 1:
        raise ValueError("Single attribute required: {}".format(kwargs))

    def decorator(cls):
        """Class decorator."""
        previous = common.attrs[cls]
        common.attrs[cls] = OrderedDict()
        for name, converter in kwargs.items():
            common.attrs[cls][name] = converter
        for name, converter in previous.items():
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
    log.info("Manually updating %r from file...", instance)
    _check_base(instance, mappable=True)

    mapper = common.get_mapper(instance)
    _check_existance(mapper, existing)

    if mapper.modified or force:
        mapper.fetch()


def update_file(instance, existing=None, force=True):
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


def synced(obj):
    """Determine if an object is already mapped to a file."""
    return bool(common.get_mapper(obj))


def _ordered(data):
    """Sort a dictionary-like object by key."""
    if data is None:
        return None
    return OrderedDict(sorted(data.items(), key=lambda pair: pair[0]))


def _check_base(obj, mappable=True):
    """Confirm an object's base class is `Mappable` as required."""
    if mappable and not synced(obj):
        raise exceptions.MappingError("{} is not mapped".format(repr(obj)))
    if not mappable and synced(obj):
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
