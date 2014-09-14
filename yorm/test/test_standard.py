#!/usr/bin/env python
# pylint:disable=R0201

"""Unit tests for the `standard` module."""


import pytest

from yorm import standard


class TestDictionary:

    """Unit tests for the `Dictionary` converter."""

    obj = {'abc': 123}

    data_value = [
        (obj, obj),
        (None, {}),
        ("key=value", {'key': "value"}),
        ("key=", {'key': ""}),
        ("key", {'key': None}),
    ]

    value_data = [
        (obj, obj),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert value == standard.Dictionary.to_value(data)

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == standard.Dictionary.to_data(value)


class TestList:

    """Unit tests for the `List` converter."""

    obj = [1, 2.3, "4", False]

    data_value = [
        (obj, obj),
        (None, []),
        ("a b c", ["a", "b", "c"]),
        ("a,b,c", ["a", "b", "c"]),
        ("abc", ["abc"]),
        ("a\nb\nc", ["a", "b", "c"]),
        (4.2, [4.2]),
    ]

    value_data = [
        (obj, obj),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert value == standard.List.to_value(data)

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == standard.List.to_data(value)


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
        assert value == standard.String.to_value(data)

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == standard.String.to_data(value)


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
        assert value == standard.Integer.to_value(data)

    def test_to_value_error(self):
        """Verify an exception is raised for unconvertible values."""
        with pytest.raises(ValueError):
            standard.Integer.to_value("abc")

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == standard.Integer.to_data(value)


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
        assert value == standard.Float.to_value(data)

    def test_to_value_error(self):
        """Verify an exception is raised for unconvertible values."""
        with pytest.raises(ValueError):
            standard.Integer.to_value("abc")

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == standard.Float.to_data(value)


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
        ("true", True),
        ("false", False),
        ("T", True),
        ("F", False),
        ("yes", True),
        ("no", False),
        ("Y", True),
        ("N", False),
        ("enabled", True),
        ("disabled", False),
        ("on", True),
        ("off", False),
        ("Hello, world!", True)
    ]

    value_data = [
        (obj, obj),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert value == standard.Boolean.to_value(data)

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == standard.Boolean.to_data(value)


if __name__ == '__main__':
    pytest.main()
