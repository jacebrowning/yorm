"""Functions and decorators."""

import uuid

from . import common
from .base import Mappable
from .mapper import Mapper

log = common.logger(__name__)

UUID = 'UUID'


def sync(*args, **kwargs):
    """Convenience function to forward calls based on arguments.

    This function will call one of:

    * `sync_object` - when given an unmapped object
    * `sync_instances` - when used as the class decorator

    Consult the signature of each call for more information.

    """
    if 'path_format' in kwargs or args and isinstance(args[0], str):
        return sync_instances(*args, **kwargs)
    else:
        return sync_object(*args, **kwargs)


def sync_object(instance, path, attrs=None, auto=True):
    """Enable YAML mapping on an object.

    :param instance: object to patch with YAML mapping behavior
    :param path: file path for dump/load
    :param attrs: dictionary of attribute names mapped to converter classes
    :param auto: automatically store attribute to file

    """
    attrs = attrs or {}

    if isinstance(instance, Mappable):
        raise common.UseageError("{} is already mapped".format(repr(instance)))

    class Mapped(Mappable, instance.__class__):

        """Original class with `Mappable` as the base."""

    instance.__class__ = Mapped

    instance.yorm_attrs = attrs or getattr(instance, 'yorm_attrs', attrs)
    instance.yorm_path = path
    instance.yorm_mapper = Mapper(instance.yorm_path)

    if not instance.yorm_mapper.exists:
        instance.yorm_mapper.create(instance)
        if auto:
            instance.yorm_mapper.store(instance, instance.yorm_attrs)
    else:
        instance.yorm_mapper.fetch(instance, instance.yorm_attrs)

    instance.yorm_mapper.auto = auto

    return instance


def sync_instances(path_format, format_spec=None, attrs=None, auto=True):
    """Class decorator to enable YAML mapping after instantiation.

    :param path_format: formatting string to create file paths for dump/load
    :param format_spec: dictionary to use for string formatting
    :param attrs: dictionary of attribute names mapped to converter classes
    :param auto: automatically store attribute to file

    """
    format_spec = format_spec or {}
    attrs = attrs or {}

    def decorator(cls):
        """Class decorator."""
        if hasattr(cls, 'yorm_attrs'):
            cls.yorm_attrs.update(attrs)
        else:
            cls.yorm_attrs = attrs

        class Mapped(Mappable, cls):

            """Original class with `Mappable` as the base."""

            def __init__(self, *_args, **_kwargs):
                super().__init__(*_args, **_kwargs)

                format_spec2 = {}
                for key, value in format_spec.items():
                    format_spec2[key] = getattr(self, value)
                if '{' + UUID + '}' in path_format:
                    format_spec2[UUID] = uuid.uuid4().hex
                format_spec2['self'] = self

                self.yorm_path = path_format.format(**format_spec2)
                self.yorm_mapper = Mapper(self.yorm_path)

                if not self.yorm_mapper.exists:
                    self.yorm_mapper.create(self)
                    if auto:
                        self.yorm_mapper.store(self, self.yorm_attrs)
                else:
                    self.yorm_mapper.fetch(self, self.yorm_attrs)

                self.yorm_mapper.auto = auto

        return Mapped

    return decorator


def attr(**kwargs):
    """Class decorator to map attributes to converters.

    :param kwargs: keyword arguments mapping attribute name to converter class

    """
    def decorator(cls):
        """Class decorator."""
        if not hasattr(cls, 'yorm_attrs'):
            cls.yorm_attrs = {}
        for name, converter in kwargs.items():
            cls.yorm_attrs[name] = converter
        return cls

    return decorator


def update(instance):
    """Synchronize changes between a mapped object and its file."""
    log.critical(instance)


def update_object(instance):
    """Synchronize changes into a mapped object from its file."""
    log.critical(instance)


def update_file(instance):
    """Synchronize changes into a mapped object's file."""
    log.critical(instance)
