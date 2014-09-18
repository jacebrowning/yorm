"""Converter classes for builtin types."""

from . import common
from .base import Converter

log = common.logger(__name__)


class Object(Converter):  # pylint: disable=W0223

    """Base class for standard types (mapped directly to YAML)."""

    @staticmethod
    def to_value(data):
        return data

    @staticmethod
    def to_data(value):
        return value


class String(Object):

    """Converter for the `str` type."""

    type = str

    @staticmethod
    def to_value(data):
        """Convert data back to a string."""
        if isinstance(data, String.type):
            return data
        elif data:
            try:
                return ', '.join(str(item) for item in data)
            except TypeError:
                return str(data)
        else:
            return ""


class Integer(Object):

    """Converter for the `int` type."""

    type = int

    @staticmethod
    def to_value(data):
        """Convert data back to an integer."""
        if isinstance(data, Integer.type):
            return data
        elif data:
            try:
                return int(data)
            except ValueError:
                return int(float(data))
        else:
            return 0


class Float(Object):

    """Converter for the `float` type."""

    type = float

    @staticmethod
    def to_value(data):
        """Convert data back to a float."""
        if isinstance(data, Float.type):
            return data
        elif data:
            return float(data)
        else:
            return 0.0


class Boolean(Object):

    """Converter for the `bool` type."""

    type = bool

    FALSY = ('false', 'f', 'no', 'n', 'disabled', 'off', '0')

    @staticmethod
    def to_value(data):
        """Convert data back to a boolean."""
        return Boolean.to_bool(data)

    @staticmethod
    def to_bool(obj):
        """Convert a boolean-like object to a boolean.

        >>> Boolean.to_bool(1)
        True

        >>> Boolean.to_bool(0)
        False

        >>> Boolean.to_bool(' True ')
        True

        >>> Boolean.to_bool('F')
        False

        """
        if isinstance(obj, str) and obj.lower().strip() in Boolean.FALSY:
            return False
        else:
            return bool(obj)


def match(data):
    """Determine the appropriate convert for new data."""
    log.trace("determining converter for: {}".format(repr(data)))
    converters = Object.__subclasses__()

    log.trace("converter options: {}".format(converters))
    for converter in converters:
        if converter.type and isinstance(data, converter.type):
            log.trace("matched: {}".format(converter))
            return converter

    if data is None:
        log.trace("default: {}".format(Object))
        return Object

    raise common.ConversionError("no converter available for: {}".format(data))
