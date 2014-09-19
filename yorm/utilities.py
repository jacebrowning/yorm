"""Functions and decorators."""

import os
import uuid

from . import common
from .base import Mappable
from .mapper import Mapper

log = common.logger(__name__)

UUID = 'UUID'


def store(instance, path, mapping=None):
    """Enable YAML mapping on an object.

    :param instance: object to patch with YAML mapping behavior
    :param path: file path for dump/load
    :param mapping: dictionary of attribute names mapped to converter classes

    """
    mapping = mapping or {}

    class Mapped(instance.__class__, Mappable):

        """Original class with `Mappable` as the base."""

    instance.__class__ = Mapped

    instance.yorm_attrs = mapping
    instance.yorm_path = path
    instance.yorm_mapper = Mapper(instance.yorm_path)

    if not os.path.exists(instance.yorm_path):
        instance.yorm_mapper.create(instance)
        instance.yorm_mapper.store(instance)
    else:
        instance.yorm_mapper.retrieve(instance)

    return instance


def store_instances(path_format, format_spec=None, mapping=None):
    """Class decorator to enable YAML mapping after instantiation.

    :param path_format: formatting string to create file paths for dump/load
    :param format_spec: dictionary to use for string formatting
    :param mapping: dictionary of attribute names mapped to converter classes

    """
    format_spec = format_spec or {}
    mapping = mapping or {}

    def decorator(cls):
        """Class decorator."""
        if hasattr(cls, 'yorm_attrs'):
            cls.yorm_attrs.update(mapping)
        else:
            cls.yorm_attrs = mapping

        class Mapped(cls, Mappable):

            """Original class with `Mappable` as the base."""

            def __init__(self, *_args, **_kwargs):
                super().__init__(*_args, **_kwargs)

                format_spec2 = {}
                for key, value in format_spec.items():
                    format_spec2[key] = getattr(self, value)
                if '{' + UUID + '}' in path_format:
                    format_spec2[UUID] = uuid.uuid4().hex

                self.yorm_path = path_format.format(**format_spec2)
                self.yorm_mapper = Mapper(self.yorm_path)

                if not os.path.exists(self.yorm_path):
                    self.yorm_mapper.create(self)
                    self.yorm_mapper.store(self)
                else:
                    self.yorm_mapper.retrieve(self)

        return Mapped

    return decorator


def map_attr(**kwargs):
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
