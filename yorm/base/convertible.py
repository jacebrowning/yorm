"""Base classes for conversion."""

import abc

from .. import common
from . import MESSAGE
from .mappable import Mappable
from .converter import Converter


log = common.logger(__name__)


class Convertible(Mappable, Converter):

    """Base class for mutable attributes."""

    @abc.abstractclassmethod
    def create_default(cls):
        """Create a default value for an attribute."""
        raise NotImplementedError(MESSAGE)

    @classmethod
    def to_value(cls, data):
        value = cls.create_default()
        value.update_value(data)
        return value

    @abc.abstractmethod
    def update_value(self, data):  # pylint: disable=E0213
        """Update the attribute's value from loaded data."""
        raise NotImplementedError(MESSAGE)

    def format_data(self):
        """Format the attribute to data optimized for dumping."""
        return self.to_data(self)
