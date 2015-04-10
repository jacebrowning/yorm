"""Base classes."""

import abc

from . import common

log = common.logger(__name__)


MAPPER = 'yorm_mapper'


class Mappable(metaclass=abc.ABCMeta):

    """Base class for objects with attributes that map to YAML."""

    def __getattribute__(self, name):
        if name == MAPPER:
            return object.__getattribute__(self, name)

        mapper = getattr(self, MAPPER, None)

        try:
            value = object.__getattribute__(self, name)
        except AttributeError:
            if mapper:
                mapper.fetch()
            value = object.__getattribute__(self, name)
        else:
            if mapper and name in mapper.attrs:
                mapper.fetch()
                value = object.__getattribute__(self, name)

        return value

    def __setattr__(self, name, value):
        mapper = getattr(self, MAPPER, None)

        if mapper and name in mapper.attrs:
            converter = mapper.attrs[name]
            value = converter.to_value(value)

        object.__setattr__(self, name, value)

        if mapper:
            log.critical(mapper.attrs)

        if mapper and name in mapper.attrs:
            if mapper.auto:
                self.yorm_mapper.store()
            else:
                log.trace("automatic storage is off")

    def __enter__(self):
        log.debug("turning off automatic storage...")
        mapper = getattr(self, MAPPER)
        mapper.auto = False

    def __exit__(self, *_):
        log.debug("turning on automatic storage...")
        mapper = getattr(self, MAPPER)
        mapper.store()


class Converter(metaclass=abc.ABCMeta):

    """Base class for attribute converters."""

    TYPE = None  # type for inferred converters (set in subclasses)
    DEFAULT = None  # default value for conversion (set in subclasses)

    @abc.abstractclassmethod
    def to_value(cls, obj):  # pylint: disable=E0213
        """Convert the loaded value back to its original attribute type."""
        raise NotImplementedError("method must be implemented in subclasses")

    @abc.abstractclassmethod
    def to_data(cls, obj):  # pylint: disable=E0213
        """Convert the attribute's value for optimal dumping to YAML."""
        raise NotImplementedError("method must be implemented in subclasses")
