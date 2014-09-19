"""Converter classes for extension types."""

import re

import yaml

from .standard import String


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
