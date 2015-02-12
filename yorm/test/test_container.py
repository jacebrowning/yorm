#!/usr/bin/env python
# pylint:disable=R0201

"""Unit tests for the `container` module."""

import pytest

from yorm.utilities import map_attr
from yorm.container import Dictionary, List
from yorm.standard import String, Integer


# sample classes ##############################################################


@map_attr(abc=Integer)
class SampleDictionary(Dictionary):

    """Sample dictionary container."""


@map_attr(var1=Integer, var2=String)
class SampleDictionaryWithInitialization(Dictionary):

    """Sample dictionary container with initialization."""

    def __init__(self, var1, var2, var3):
        super().__init__()
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3


@map_attr(all=String)
class StringList(List):

    """Sample list container."""

    # TODO: this shouldn't be required for the tests to pass
    yorm_attrs = {'all': String}


class UnknownList(List):

    """Sample list container."""


# tests #######################################################################


class TestDictionary:

    """Unit tests for the `Dictionary` container."""

    obj = {'abc': 123}

    data_value = [
        (obj, obj),
        (None, {'abc': 0}),
        ("key=value", {'key': "value", 'abc': 0}),
        ("key=", {'key': "", 'abc': 0}),
        ("key", {'key': None, 'abc': 0}),
    ]

    value_data = [
        (obj, obj),
    ]

    def setup_method(self, _):
        """Reset the class' mapped attributes before each test."""
        SampleDictionary.yorm_attrs = {'abc': Integer}

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert value == SampleDictionary.to_value(data)

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == SampleDictionary.to_data(value)

    def test_not_implemented(self):
        """Verify `Dictionary` cannot be used directly."""
        with pytest.raises(NotImplementedError):
            Dictionary.to_value(None)
        with pytest.raises(NotImplementedError):
            Dictionary.to_data(None)

    def test_dict_as_object(self):
        """Verify a `Dictionary` can be used as an attribute."""
        dictionary = SampleDictionaryWithInitialization(1, 2, 3.0)
        value = {'var1': 1, 'var2': '2'}
        value2 = dictionary.to_value(dictionary)
        assert value == value2
        # keys are not accesible as attributes
        assert not hasattr(value2, 'var1')
        assert not hasattr(value2, 'var2')
        assert not hasattr(value2, 'var3')


class TestList:

    """Unit tests for the `List` container."""

    obj = ["a", "b", "c"]

    data_value = [
        (obj, obj),
        (None, []),
        ("a b c", ["a", "b", "c"]),
        ("a,b,c", ["a", "b", "c"]),
        ("abc", ["abc"]),
        ("a\nb\nc", ["a", "b", "c"]),
        (4.2, ['4.2']),
    ]

    value_data = [
        (obj, obj),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert value == StringList.to_value(data)

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == StringList.to_data(value)

    def test_item_type(self):
        """Verify list item type can be determined."""
        assert String == StringList.item_type

    def test_item_type_none(self):
        """Verify list item type defaults to None."""
        assert None is UnknownList.item_type

    def test_not_implemented(self):
        """Verify `List` cannot be used directly."""
        with pytest.raises(NotImplementedError):
            List.to_value(None)
        with pytest.raises(NotImplementedError):
            List.to_data(None)
        with pytest.raises(NotImplementedError):
            UnknownList.to_value(None)
        with pytest.raises(NotImplementedError):
            UnknownList.to_data(None)


if __name__ == '__main__':
    pytest.main()
