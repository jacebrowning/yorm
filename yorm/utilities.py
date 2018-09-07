"""Functions to interact with mapped classes and instances."""

import inspect
import logging
import string
import glob
import types

import parse

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


class GlobFormatter(string.Formatter):
    """Uses '*' for all unknown fields."""

    WILDCARD = object()

    def get_field(self, field_name, args, kwargs):
        try:
            return super().get_field(field_name, args, kwargs)
        except (KeyError, IndexError, AttributeError):
            return self.WILDCARD, None

    def get_value(self, key, args, kwargs):
        try:
            return super().get_value(key, args, kwargs)
        except (KeyError, IndexError, AttributeError):
            return self.WILDCARD

    def convert_field(self, value, conversion):
        if value is self.WILDCARD:
            return self.WILDCARD
        else:
            return super().convert_field(value, conversion)

    def format_field(self, value, format_spec):
        if value is self.WILDCARD:
            return '*'
        else:
            return super().format_field(value, format_spec)


def _unpack_parsed_fields(pathfields):
    return {
        (k[len('self.'):] if k.startswith('self.') else k): v
        for k, v in pathfields.items()
    }


def match(cls_or_path, _factory=None, **kwargs):
    """Yield all matching mapped objects.

    Can be used two ways:

    * With a YORM-decorated class, optionally with a factory callable
    * With a Python 3-style string template and a factory callable

    The factory callable must accept keyword arguments, extracted from the file
    name merged with those passed to match(). If no factory is given, the class
    itself is used as the factory (same signature).

    Keyword arguments are used to filter objects. Filtering is only done by
    filename, so only fields that are part of the path_format can be filtered
    against.

    """
    if isinstance(cls_or_path, type):
        path_format = common.path_formats[cls_or_path]
        # Let KeyError fail through
        if _factory is None:
            _factory = cls_or_path
    else:
        path_format = cls_or_path
        if _factory is None:
            raise TypeError("Factory must be given if a path format is given")

    gf = GlobFormatter()
    mock = types.SimpleNamespace(**kwargs)

    kwargs['self'] = mock
    posix_pattern = gf.vformat(path_format, (), kwargs.copy())
    del kwargs['self']
    py_pattern = parse.compile(path_format)

    for filename in glob.iglob(posix_pattern):
        pathfields = py_pattern.parse(filename).named
        fields = _unpack_parsed_fields(pathfields)
        fields.update(kwargs)
        yield _factory(**fields)


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


def _instantiate(class_or_instance, *args, **kwargs):
    if inspect.isclass(class_or_instance):
        instance = class_or_instance(*args, **kwargs)
    else:
        assert not args
        instance = class_or_instance

    return instance
