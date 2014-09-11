"""Converter classes for builtin types."""

from .base import Converter


class _Standard(Converter):  # pylint: disable=W0223

    """Base class for standard types (mapped directly to YAML)."""

    @staticmethod
    def to_data(value):
        return value


class Dictionary(_Standard):

    """Converter for the `dict` type."""

    @staticmethod
    def to_value(data):
        """Convert data back to a dictionary."""
        if isinstance(data, dict):
            return data
        else:
            return {}


class List(_Standard):

    """Converter for the `list` type."""

    @staticmethod
    def to_value(data):
        """Convert data back to a list."""
        if isinstance(data, list):
            return data
        elif isinstance(data, str):
            text = data.strip()
            if ',' in text and ' ' not in text:
                return text.split(',')
            else:
                return text.split()
        else:
            return []


class String(_Standard):

    """Converter for the `str` type."""

    @staticmethod
    def to_value(data):
        """Convert data back to a string."""
        if isinstance(data, str):
            return data
        elif data:
            try:
                return ', '.join(str(item) for item in data)
            except TypeError:
                return str(data)
        else:
            return ""


class Integer(_Standard):

    """Converter for the `int` type."""

    @staticmethod
    def to_value(data):
        """Convert data back to an integer."""
        if isinstance(data, int):
            return data
        elif data:
            try:
                return int(data)
            except ValueError:
                return int(float(data))
        else:
            return 0


class Float(_Standard):

    """Converter for the `float` type."""

    @staticmethod
    def to_value(data):
        """Convert data back to a float."""
        if isinstance(data, float):
            return data
        elif data:
            return float(data)
        else:
            return 0.0


class Boolean(_Standard):

    """Converter for the `bool` type."""

    FALSY = ('false', 'f', 'no', 'disabled', '0')

    @staticmethod
    def to_value(data):
        """Convert data back to a boolean."""
        return Boolean.to_bool(data)

    @staticmethod
    def to_bool(obj):
        """Convert a boolean-like object to a boolean.

        >>> to_bool(1)
        True

        >>> to_bool(0)
        False

        >>> to_bool(' True ')
        True

        >>> to_bool('F')
        False

        """
        if isinstance(obj, str) and obj.lower().strip() in Boolean.FALSY:
            return False
        else:
            return bool(obj)
