"""Base classes."""

import abc


class Converter(metaclass=abc.ABCMeta):  # pylint:disable=R0921

    """Object attribute that is dumped as YAML."""

    @staticmethod
    @abc.abstractmethod
    def to_value(obj):
        """Convert the loaded value back to its original attribute type."""

    @staticmethod
    @abc.abstractmethod
    def to_data(obj):
        """Convert the attribute's value for optimal dumping to YAML."""
