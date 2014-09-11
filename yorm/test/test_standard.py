"""Unit tests for the `standard` module."""

import pytest
# pylint:disable=R0201

from yorm import standard


class TestDictionary:

    """Unit tests for the `Dictionary` converter."""

    obj = {'abc': 123}

    data_value = [
        (obj, obj),
        (None, {}),
    ]

    value_data = [
        (obj, obj),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert standard.Dictionary.to_value(data) == value

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert standard.Dictionary.to_data(value) == data


class TestList:

    """Unit tests for the `List` converter."""

    obj = [1, 2.3, "4", False]

    data_value = [
        (obj, obj),
        (None, []),
        ("a b c", ["a", "b", "c"]),
        ("a,b,c", ["a", "b", "c"]),
    ]

    value_data = [
        (obj, obj),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert standard.List.to_value(data) == value

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert standard.List.to_data(value) == data


class TestString:

    """Unit tests for the `String` converter."""

    obj = "Hello, world!"

    data_value = [
        (obj, obj),
        (None, ""),
        (1, "1"),
        (4.2, "4.2"),
        (['a', 'b', 'c'], "a, b, c"),
    ]

    value_data = [
        (obj, obj),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert standard.String.to_value(data) == value

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert standard.String.to_data(value) == data


class TestInteger:

    """Unit tests for the `Integer` converter."""

    obj = 42

    data_value = [
        (obj, obj),
        (None, 0),
        ("1", 1),
        ("1.1", 1),
    ]

    value_data = [
        (obj, obj),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert standard.Integer.to_value(data) == value

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert standard.Integer.to_data(value) == data


class TestFloat:

    """Unit tests for the `Float` converter."""

    obj = 4.2

    data_value = [
        (obj, obj),
        (None, 0.0),
        ("1.0", 1.0),
        ("1.1", 1.1),
    ]

    value_data = [
        (obj, obj),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert standard.Float.to_value(data) == value

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert standard.Float.to_data(value) == data


class TestBoolean:

    """Unit tests for the `Boolean` converter."""

    obj = True

    data_value = [
        (obj, obj),
        (None, False),
        (0, False),
        (1, True),
        ("", False),
        ("True", True),
        ("False", False),
        ("false", False),
        ("t", True),
        ("Hello, world!", True)
    ]

    value_data = [
        (obj, obj),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert standard.Boolean.to_value(data) == value

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert standard.Boolean.to_data(value) == data
