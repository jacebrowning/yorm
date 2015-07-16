"""Base classes for converters."""

import abc

from .. import common


log = common.logger(__name__)


class Converter(metaclass=abc.ABCMeta):

    """Base class for immutable attribute converters."""

    @abc.abstractclassmethod
    def create_default(cls):
        """Create a default value for an attribute."""
        raise NotImplementedError(common.OVERRIDE_MESSAGE)

    @abc.abstractclassmethod
    def to_value(cls, data):
        """Convert loaded data to an attribute's value."""
        raise NotImplementedError(common.OVERRIDE_MESSAGE)

    @abc.abstractclassmethod
    def to_data(cls, value):
        """Convert an attribute to data optimized for dumping."""
        raise NotImplementedError(common.OVERRIDE_MESSAGE)
