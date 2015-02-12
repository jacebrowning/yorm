"""Converter classes for builtin types."""

from . import common
from .base import Converter

log = common.logger(__name__)


class Object(Converter):  # pylint: disable=W0223

    """Base class for standard types (mapped directly to YAML)."""

    @classmethod
    def to_value(cls, obj):
        return obj

    @classmethod
    def to_data(cls, obj):
        return cls.to_value(obj)


class String(Object):

    """Converter for the `str` type."""

    TYPE = str
    DEFAULT = ""

    @classmethod
    def to_value(cls, obj):
        if isinstance(obj, cls.TYPE):
            return obj
        elif obj:
            try:
                return ', '.join(str(item) for item in obj)
            except TypeError:
                return str(obj)
        else:
            return cls.DEFAULT


class Integer(Object):

    """Converter for the `int` type."""

    TYPE = int
    DEFAULT = 0

    @classmethod
    def to_value(cls, obj):
        if isinstance(obj, cls.TYPE):
            return obj
        elif obj:
            try:
                return int(obj)
            except ValueError:
                return int(float(obj))
        else:
            return cls.DEFAULT


class Float(Object):

    """Converter for the `float` type."""

    TYPE = float
    DEFAULT = 0.0

    @classmethod
    def to_value(cls, obj):
        if isinstance(obj, cls.TYPE):
            return obj
        elif obj:
            return float(obj)
        else:
            return cls.DEFAULT


class Boolean(Object):

    """Converter for the `bool` type."""

    TYPE = bool
    DEFAULT = False

    FALSY = ('false', 'f', 'no', 'n', 'disabled', 'off', '0')

    @classmethod
    def to_value(cls, obj):
        if isinstance(obj, str) and obj.lower().strip() in cls.FALSY:
            return False
        elif obj is not None:
            return bool(obj)
        else:
            return cls.DEFAULT


def match(name, data, nested=False):
    """Determine the appropriate converter for new data."""
    nested = " nested" if nested else ""
    msg = "determining converter for new%s: '%s' = %r"
    log.debug(msg, nested, name, repr(data))

    converters = Object.__subclasses__()
    log.trace("converter options: {}".format(converters))

    for converter in converters:
        if converter.TYPE and type(data) == converter.TYPE:
            log.debug("matched converter: %s", converter)
            log.info("new%s attribute: %s", nested, name)
            return converter

    if data is None or isinstance(data, (dict, list)):
        log.info("default converter: %s", Object)
        log.warn("new%s attribute with unknown type: %s", nested, name)
        return Object

    raise common.ConversionError("no converter available for: {}".format(data))
