"""Base classes for conversion."""

import abc

from .. import common
from . import MESSAGE


log = common.logger(__name__)


class Convertible(metaclass=abc.ABCMeta):

    """Base class for attribute converters."""

    def __new__(cls, *args, **kwargs):
        if cls is Convertible:
            msg = "Convertible class must be subclassed to use"
            raise NotImplementedError(msg)
        return super().__new__(cls, *args, **kwargs)

    @abc.abstractmethod
    def update_value(self, data):  # pylint: disable=E0213
        """Update the object's value from the loaded data."""
        raise NotImplementedError(MESSAGE)

    @abc.abstractmethod
    def format_data(self):  # pylint: disable=E0213
        """Convert the object's value to data optimized for dumping."""
        raise NotImplementedError(MESSAGE)
