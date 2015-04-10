"""Base classes for conversion."""

import abc

from .. import common

log = common.logger(__name__)


class Convertible(metaclass=abc.ABCMeta):

    """Base class for attribute converters."""

    TYPE = None  # type for inferred converters (set in subclasses)
    DEFAULT = None  # default value for conversion (set in subclasses)

    @abc.abstractclassmethod
    def to_value(cls, obj):  # pylint: disable=E0213
        """Convert the loaded value back to its original attribute type."""
        raise NotImplementedError("method must be implemented in subclasses")

    @abc.abstractclassmethod
    def to_data(cls, obj):  # pylint: disable=E0213
        """Convert the attribute's value to something easily serialized."""
        raise NotImplementedError("method must be implemented in subclasses")
