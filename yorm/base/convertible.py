"""Base classes for conversion."""

import abc

from .. import common
from . import MESSAGE


log = common.logger(__name__)


class Convertible(metaclass=abc.ABCMeta):

    """Base class for attribute converters."""

    @abc.abstractclassmethod
    def to_value(cls, obj):
        """Convert the loaded data back into the attribute's type."""
        raise NotImplementedError(MESSAGE)

    @abc.abstractclassmethod
    def to_data(cls, obj):
        """Convert the attribute's value to data optimized for dumping."""
        raise NotImplementedError(MESSAGE)
