"""Converter classes for builtin types."""

from . import common
from .base import Converter

log = common.logger(__name__)


class Object(Converter):  # pylint: disable=W0223

    """Base class for standard types (mapped directly to YAML)."""

    @classmethod
    def to_value(cls, data):
        return data

    @classmethod
    def to_data(cls, value):
        return value


class Dictionary(Object):

    """Converter for the `dict` type."""

    type = dict
    yorm_attrs = {}

    @classmethod
    def to_value(cls, data):
        """Convert data back to a dictionary."""
        value = {}

        for name, data in cls.to_dict(data).items():
            try:
                converter = cls.yorm_attrs[name]
            except KeyError:
                converter = match(data)
                log.info("new attribute: {}".format(name))
                cls.yorm_attrs[name] = converter
            value[name] = converter.to_value(data)

        return value

    @classmethod
    def to_data(cls, value):
        """Convert value to a dictionary."""
        data = {}

        for name, converter in cls.yorm_attrs.items():
            data[name] = converter.to_data(value.get(name, None))

        return data

    @staticmethod
    def to_dict(obj):
        """Convert a dictionary-like object to a dictionary.

        >>> Dictionary.to_dict({'key': 42})
        {'key': 42}

        >>> Dictionary.to_dict("key=42")
        {'key': '42'}

        >>> Dictionary.to_dict("key")
        {'key': None}

        >>> Dictionary.to_dict(None)
        {}

        """
        if isinstance(obj, Dictionary.type):
            return obj
        elif isinstance(obj, str):
            text = obj.strip()
            parts = text.split('=')
            if len(parts) == 2:
                return {parts[0]: parts[1]}
            else:
                return {text: None}
        else:
            return {}


class List(Object):

    """Converter for the `list` type."""

    type = list

    @classmethod
    def to_value(cls, data):
        """Convert data back to a list."""
        if isinstance(data, List.type):
            return data
        elif isinstance(data, str):
            text = data.strip()
            if ',' in text and ' ' not in text:
                return text.split(',')
            else:
                return text.split()
        elif data is not None:
            return [data]
        else:
            return []


class String(Object):

    """Converter for the `str` type."""

    type = str

    @classmethod
    def to_value(cls, data):
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

    @classmethod
    def to_value(cls, data):
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

    @classmethod
    def to_value(cls, data):
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

    @classmethod
    def to_value(cls, data):
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
