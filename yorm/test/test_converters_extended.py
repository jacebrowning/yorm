#!/usr/bin/env python
# pylint:disable=R0201,R0901

"""Unit tests for the `extended` module."""

import pytest

from yorm.utilities import attr
from yorm.converters.standard import Integer, String, Float
from yorm.converters.extended import Markdown, AttributeDictionary, SortedList


@attr(var1=Integer, var2=String)
class SampleAttributeDictionary(AttributeDictionary):

    """Sample dictionary container with initialization."""

    def __init__(self, var1, var2, var3):
        super().__init__()
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3


@attr(all=Float)
class SampleSortedList(SortedList):

    """Sample sorted list container."""


class UnknownSortedList(SortedList):

    """Sample list container."""


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
        assert value == Markdown.to_value(data)

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == Markdown.to_data(value)


class TestAttributeDictionary:

    """Unit tests for the `AttributeDictionary` container."""

    def test_not_implemented(self):
        """Verify `AttributeDictionary` cannot be used directly."""
        with pytest.raises(NotImplementedError):
            AttributeDictionary.to_value(None)
        with pytest.raises(NotImplementedError):
            AttributeDictionary.to_data(None)

    def test_attribute_access(self):
        """Verify `AttributeDictionary` keys are available as attributes."""
        obj = SampleAttributeDictionary(1, 2, 3.0)
        value = {'var1': 1, 'var2': '2'}
        value2 = obj.to_value(obj)
        assert value == value2
        assert 1 == value2.var1
        assert '2' == value2.var2
        assert not hasattr(value2, 'var3')  # lost in conversion


class TestSortedList:

    """Unit tests for the `SortedList` container."""

    def test_not_implemented(self):
        """Verify `SortedList` cannot be used directly."""
        with pytest.raises(NotImplementedError):
            SortedList.to_value(None)
        with pytest.raises(NotImplementedError):
            SortedList.to_data(None)
        with pytest.raises(NotImplementedError):
            UnknownSortedList.to_value(None)
        with pytest.raises(NotImplementedError):
            UnknownSortedList.to_data(None)

    def test_sorted_result(self):
        """Verify `SortedList` sorts the resulting data."""
        obj = SampleSortedList([4, 2, 0, 1, 3])
        data = [0.0, 1.0, 2.0, 3.0, 4.0]
        data2 = obj.to_data(obj)
        assert data == data2


if __name__ == '__main__':
    pytest.main()
