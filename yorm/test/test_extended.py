#!/usr/bin/env python
# pylint:disable=R0201

"""Unit tests for the `extended` module."""

import pytest

from yorm import extended


class TestMarkdown:

    """Unit tests for the `Markdown` converter."""

    obj = "This is **the** sentence."

    data_value = [
        (obj, obj),
        (None, ""),
        (['a', 'b', 'c'], "a, b, c"),
        ("This is\na sentence.", "This is a sentence."),
        ("Sentence one.\nSentence two.", "Sentence one. Sentence two."),
    ]

    value_data = [
        (obj, obj + '\n'),
        ("Sentence one. Sentence two.", "Sentence one.\nSentence two.\n"),
        ("", ""),
        (" \t ", ""),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert value == extended.Markdown.to_value(data)

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == extended.Markdown.to_data(value)

if __name__ == '__main__':
    pytest.main()
