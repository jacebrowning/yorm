"""Converter classes for extensions to builtin types."""

import re

import yaml

from .standard import String, Integer, Float, Boolean
from .containers import Dictionary, List


# standard types with None as a default #######################################


class NoneString(String):

    """Converter for the `str` type with `None` as default."""

    DEFAULT = None


class NoneInteger(Integer):

    """Converter for the `int` type with `None` as default."""

    DEFAULT = None


class NoneFloat(Float):

    """Converter for the `float` type with `None` as default."""

    DEFAULT = None


class NoneBoolean(Boolean):

    """Converter for the `bool` type with `None` as default."""

    DEFAULT = None


# standard types with additional behavior #####################################


class _Literal(str):

    """Custom type for strings which should be dumped in the literal style."""

    @staticmethod
    def representer(dumper, data):
        """Return a custom dumper that formats `str` in the literal style."""
        return dumper.represent_scalar('tag:yaml.org,2002:str', data,
                                       style='|' if data else '')

yaml.add_representer(_Literal, _Literal.representer)


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
        return Markdown.join(value)

    @staticmethod
    def join(text):
        r"""Convert single newlines (ignored by Markdown) to spaces.

        >>> Markdown.join("abc\n123")
        'abc 123'

        >>> Markdown.join("abc\n\n123")
        'abc\n\n123'

        >>> Markdown.join("abc \n123")
        'abc 123'

        """
        return Markdown.REGEX_MARKDOWN_SPACES.sub(r'\1 \3', text).strip()

    @classmethod
    def to_data(cls, obj):
        """Break a string at sentences and dump as a literal string."""
        value = String.to_value(obj)
        data = String.to_data(value)
        split = Markdown.split(data)
        return _Literal(split)

    @staticmethod
    def split(text, end='\n'):
        r"""Replace sentence boundaries with newlines and append a newline.

        :param text: string to line break at sentences
        :param end: appended to the end of the update text

        >>> Markdown.split("Hello, world!", end='')
        'Hello, world!'

        >>> Markdown.split("Hello, world! How are you? I'm fine. Good.")
        "Hello, world!\nHow are you?\nI'm fine.\nGood.\n"

        """
        stripped = text.strip()
        if stripped:
            return Markdown.REGEX_SENTENCE_BOUNDARIES.sub('\n', stripped) + end
        else:
            return ''

# container types with additional behavior ####################################


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
            data.append(cls.item_type.to_data(item))

        return data
