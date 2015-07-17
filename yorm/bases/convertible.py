"""Base classes for convertible attributes."""

from abc import ABCMeta, abstractmethod

from .. import common
from . import Mappable, Converter


log = common.logger(__name__)


class Convertible(Mappable, Converter, metaclass=ABCMeta):  # pragma: no cover (abstract)

    """Base class for mutable attributes."""

    @classmethod
    def create_default(cls):
        return cls.__new__(cls)

    @classmethod
    def to_value(cls, data):
        value = cls.create_default()
        value.update_value(data)
        return value

    @abstractmethod
    def update_value(self, data, match=None):  # pylint: disable=E0213,
        """Update the attribute's value from loaded data."""
        raise NotImplementedError(common.OVERRIDE_MESSAGE)

    def format_data(self):
        """Format the attribute to data optimized for dumping."""
        return self.to_data(self)
