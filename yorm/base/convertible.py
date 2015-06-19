"""Base classes for conversion."""

import abc

from .. import common
from . import MESSAGE
from .converter import Converter


log = common.logger(__name__)


class Convertible(Converter):  # pragma: no cover (abstract)

    """Base class for mutable attributes."""

    @classmethod
    def to_value(cls, data):
        value = cls.create_default()
        value.update_value(data)
        return value

    @abc.abstractmethod
    def update_value(self, data, match=None):  # pylint: disable=E0213,
        """Update the attribute's value from loaded data."""
        raise NotImplementedError(MESSAGE)

    def format_data(self):
        """Format the attribute to data optimized for dumping."""
        return self.to_data(self)
