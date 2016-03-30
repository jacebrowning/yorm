"""Converter classes for extensions to builtin types."""

import re

from .standard import String, Integer, Float, Boolean
from .containers import Dictionary, List
from ._representers import LiteralString


# NULLABLE BUILTINS ############################################################


class NullableString(String):
    """Converter for the `str` type with `None` as default."""

    DEFAULT = None


class NullableInteger(Integer):
    """Converter for the `int` type with `None` as default."""

    DEFAULT = None


class NullableFloat(Float):
    """Converter for the `float` type with `None` as default."""

    DEFAULT = None


class NullableBoolean(Boolean):
    """Converter for the `bool` type with `None` as default."""

    DEFAULT = None


# CUSTOM TYPES #################################################################


class Markdown(String):
    """Converter for a `str` type that contains Markdown."""

    REGEX_MARKDOWN_SPACES = re.compile(r"""

    ([^\n ])  # any character but a newline or space

    (\ ?\n)   # optional space + single newline

    (?!       # none of the following:

      (?:\s)       # whitespace
      |
      (?:[-+*]\s)  # unordered list separator + whitespace
      |
      (?:\d+\.\s)  # number + period + whitespace

    )

    ([^\n])  # any character but a newline

    """, re.VERBOSE | re.IGNORECASE)

    # based on: http://en.wikipedia.org/wiki/Sentence_boundary_disambiguation
    REGEX_SENTENCE_BOUNDARIES = re.compile(r"""

    (            # one of the following:

      (?<=[a-z)][.?!])      # lowercase letter + punctuation
      |
      (?<=[a-z0-9][.?!]\")  # lowercase letter/number + punctuation + quote

    )

    (\s)          # any whitespace

    (?=\"?[A-Z])  # optional quote + an upppercase letter

    """, re.VERBOSE)

    @classmethod
    def to_value(cls, obj):
        """Join non-meaningful line breaks."""
        value = String.to_value(obj)
        return cls._join(value)

    @classmethod
    def to_data(cls, obj):
        """Break a string at sentences and dump as a literal string."""
        value = String.to_value(obj)
        data = String.to_data(value)
        split = cls._split(data)
        return LiteralString(split)

    @classmethod
    def _join(cls, text):
        r"""Convert single newlines (ignored by Markdown) to spaces.

        >>> Markdown._join("abc\n123")
        'abc 123'

        >>> Markdown._join("abc\n\n123")
        'abc\n\n123'

        >>> Markdown._join("abc \n123")
        'abc 123'

        """
        return cls.REGEX_MARKDOWN_SPACES.sub(r'\1 \3', text).strip()

    @classmethod
    def _split(cls, text, end='\n'):
        r"""Replace sentence boundaries with newlines and append a newline.

        :param text: string to line break at sentences
        :param end: appended to the end of the update text

        >>> Markdown._split("Hello, world!", end='')
        'Hello, world!'

        >>> Markdown._split("Hello, world! How are you? I'm fine. Good.")
        "Hello, world!\nHow are you?\nI'm fine.\nGood.\n"

        """
        stripped = text.strip()
        if stripped:
            return cls.REGEX_SENTENCE_BOUNDARIES.sub('\n', stripped) + end
        else:
            return ''


# CUSTOM CONTAINERS ############################################################


class AttributeDictionary(Dictionary):
    """Dictionary converter with keys available as attributes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    @classmethod
    def create_default(cls):
        """Create an uninitialized object with keys as attributes."""
        if cls is AttributeDictionary:
            msg = "AttributeDictionary class must be subclassed to use"
            raise NotImplementedError(msg)

        obj = cls.__new__(cls)
        obj.__dict__ = obj
        return obj


class SortedList(List):
    """List converter that is sorted on disk."""

    @classmethod
    def create_default(cls):
        """Create an uninitialized object."""
        if cls is SortedList:
            msg = "SortedList class must be subclassed to use"
            raise NotImplementedError(msg)
        if not cls.item_type:
            msg = "SortedList subclass must specify item type"
            raise NotImplementedError(msg)

        return cls.__new__(cls)

    @classmethod
    def to_data(cls, obj):
        """Convert all attribute values for optimal dumping to YAML."""
        value = cls.to_value(obj)

        data = []

        for item in sorted(value):
            data.append(cls.item_type.to_data(item))  # pylint: disable=no-member

        return data
