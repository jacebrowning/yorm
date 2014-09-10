"""Base classes."""

import abc


class Mappable(metaclass=abc.ABCMeta):  # pylint:disable=R0921

    """Base class for objects with attributes that map to YAML."""


class Converter(metaclass=abc.ABCMeta):  # pylint:disable=R0921

    """Base class for attribute converters."""

    @staticmethod
    @abc.abstractmethod
    def to_value(obj):
        """Convert the loaded value back to its original attribute type."""

    @staticmethod
    @abc.abstractmethod
    def to_data(obj):
        """Convert the attribute's value for optimal dumping to YAML."""
