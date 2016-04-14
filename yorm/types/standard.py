"""Convertible classes for builtin immutable types."""

import logging

from .. import exceptions
from ..bases import Converter

log = logging.getLogger(__name__)


class Object(Converter):
    """Base class for immutable types."""

    TYPE = None  # type for inferred types (set in subclasses)
    DEFAULT = None  # default value for conversion (set in subclasses)

    @classmethod
    def create_default(cls):
        return cls.DEFAULT

    @classmethod
    def to_value(cls, obj):
        return obj

    @classmethod
    def to_data(cls, obj):
        return cls.to_value(obj)


class String(Object):
    """Convertible for the `str` type."""

    TYPE = str
    DEFAULT = ""

    @classmethod
    def to_value(cls, obj):
        if isinstance(obj, cls.TYPE):
            return obj
        elif obj is True:
            return "true"
        elif obj is False:
            return "false"
        elif obj:
            try:
                return ', '.join(str(item) for item in obj)
            except TypeError:
                return str(obj)
        else:
            return cls.DEFAULT

    @classmethod
    def to_data(cls, obj):
        value = cls.to_value(obj)
        return cls._optimize_for_quoting(value)

    @staticmethod
    def _optimize_for_quoting(value):
        if value == "true":
            return True
        if value == "false":
            return False
        for number_type in (int, float):
            try:
                return number_type(value)
            except (TypeError, ValueError):
                continue
        return value


class Integer(Object):
    """Convertible for the `int` type."""

    TYPE = int
    DEFAULT = 0

    @classmethod
    def to_value(cls, obj):
        if all((isinstance(obj, cls.TYPE),
                obj is not True,
                obj is not False)):
            return obj
        elif obj:
            try:
                return int(obj)
            except ValueError:
                return int(float(obj))
        else:
            return cls.DEFAULT


class Float(Object):
    """Convertible for the `float` type."""

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
    """Convertible for the `bool` type."""

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
    msg = "Determining converter for new%s: '%s' = %r"
    log.debug(msg, nested, name, repr(data))

    types = Object.__subclasses__()  # pylint: disable=no-member
    log.trace("Converter options: {}".format(types))

    for converter in types:
        if converter.TYPE and type(data) == converter.TYPE:  # pylint: disable=unidiomatic-typecheck
            log.debug("Matched converter: %s", converter)
            log.info("New%s attribute: %s", nested, name)
            return converter

    if data is None or isinstance(data, (dict, list)):
        log.info("Default converter: %s", Object)
        log.warning("New%s attribute with unknown type: %s", nested, name)
        return Object

    msg = "No converter available for: {}".format(data)
    raise exceptions.FileContentError(msg)
