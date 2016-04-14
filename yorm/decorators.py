"""Functions to enable mapping on classes and instances."""

import uuid
from collections import OrderedDict
import logging

from . import common
from .bases.mappable import patch_methods
from .mapper import Mapper

log = logging.getLogger(__name__)


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


def sync_object(instance, path, attrs=None, **kwargs):
    """Enable YAML mapping on an object.

    :param instance: object to patch with YAML mapping behavior
    :param path: file path for dump/parse
    :param attrs: dictionary of attribute names mapped to converter classes

    :param auto_create: automatically create the file to save attributes
    :param auto_save: automatically save attribute changes to the file
    :param auto_track: automatically add new attributes from the file

    """
    log.info("Mapping %r to %s...", instance, path)

    common.get_mapper(instance, expected=False)
    patch_methods(instance)

    attrs = _ordered(attrs) or common.attrs[instance.__class__]
    mapper = Mapper(instance, path, attrs, **kwargs)

    if mapper.missing:
        if mapper.auto_create:
            mapper.create()
            if mapper.auto_save:
                mapper.save()
                mapper.load()
    else:
        mapper.load()

    common.set_mapper(instance, mapper)
    log.info("Mapped %r to %s", instance, path)

    return instance


def sync_instances(path_format, format_spec=None, attrs=None, **kwargs):
    """Class decorator to enable YAML mapping after instantiation.

    :param path_format: formatting string to create file paths for dump/parse
    :param format_spec: dictionary to use for string formatting
    :param attrs: dictionary of attribute names mapped to converter classes

    :param auto_create: automatically create the file to save attributes
    :param auto_save: automatically save attribute changes to the file
    :param auto_track: automatically add new attributes from the file

    """
    format_spec = format_spec or {}
    attrs = attrs or OrderedDict()

    def decorator(cls):
        """Class decorator to map instances to files."""
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


def _ordered(data):
    """Sort a dictionary-like object by key."""
    if data is None:
        return None
    return OrderedDict(sorted(data.items(), key=lambda pair: pair[0]))
