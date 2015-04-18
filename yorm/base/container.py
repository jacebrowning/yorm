"""Base classes for containers."""

import abc

from .. import common
from . import MESSAGE
from .convertible import Convertible
from .mappable import Mappable


log = common.logger(__name__)


class Container(Convertible, Mappable):

    """Base class for mutable types."""

    @abc.abstractmethod
    def apply(self, data):  # pylint: disable=E0213
        """Update the container's values with the loaded data."""
        raise NotImplementedError(MESSAGE)

    def format(self):  # pylint: disable=E0213
        """Convert the container's values to data optimized for dumping."""
        return self.to_data(self)

    @abc.abstractclassmethod
    def to_data(cls, value):
        raise NotImplementedError(MESSAGE)
