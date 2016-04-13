"""Converter classes."""

from abc import ABCMeta, abstractclassmethod, abstractmethod
import logging

from .. import common
from . import Mappable

log = logging.getLogger(__name__)


class Converter(metaclass=ABCMeta):
    """Base class for attribute converters."""

    @abstractclassmethod
    def create_default(cls):
        """Create a default value for an attribute."""
        raise NotImplementedError(common.OVERRIDE_MESSAGE)

    @abstractclassmethod
    def to_value(cls, data):
        """Convert parsed data to an attribute's value."""
        raise NotImplementedError(common.OVERRIDE_MESSAGE)

    @abstractclassmethod
    def to_data(cls, value):
        """Convert an attribute to data optimized for dumping."""
        raise NotImplementedError(common.OVERRIDE_MESSAGE)


class Container(Mappable, Converter, metaclass=ABCMeta):
    """Base class for mutable attribute converters."""

    @classmethod
    def create_default(cls):
        return cls.__new__(cls)

    @classmethod
    def to_value(cls, data):
        value = cls.create_default()
        value.update_value(data, auto_track=True)
        return value

    @abstractmethod
    def update_value(self, data, *, auto_track):  # pragma: no cover (abstract method)
        """Update the attribute's value from parsed data."""
        raise NotImplementedError(common.OVERRIDE_MESSAGE)

    def format_data(self):
        """Format the attribute to data optimized for dumping."""
        return self.to_data(self)
