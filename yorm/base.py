"""Base classes."""

import abc


class Yattribute(metaclass=abc.ABCMeta):

    """Object attribute that is dumped as YAML."""

    @abc.abstractstaticmethod
    def to_value(obj):
        """Convert the loaded value back to its original attribute type."""

    @abc.abstractstaticmethod
    def to_data(obj):
        """Convert the attribute's value for optimal dumping to YAML."""
