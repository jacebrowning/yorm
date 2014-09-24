#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201

"""Unit tests for the `base` module."""

import pytest
import logging

from yorm.base import Mappable, Converter, Dictionary, List
from yorm.mapper import Mapper
from yorm.utilities import map_attr
from yorm.standard import String, Integer, Boolean


class MockMapper(Mapper):

    """Mapped file with stubbed file IO."""

    def __init__(self, path):
        super().__init__(path)
        self._mock_file = None

    def read(self):
        text = self._mock_file
        logging.debug("mock read:\n{}".format(text.strip()))
        return text

    def write(self, text):
        logging.debug("mock write:\n{}".format(text.strip()))
        self._mock_file = text


# sample classes ##############################################################


class SampleMappable(Mappable):

    """Sample mappable class with hard-coded settings."""

    def __init__(self):
        logging.debug("initializing sample...")
        self.var1 = None
        self.var2 = None
        self.var3 = None
        logging.debug("sample initialized")

        self.yorm_path = "mock/path/to/sample.yml"
        self.yorm_attrs = {'var1': String,
                           'var2': Integer,
                           'var3': Boolean}
        self.yorm_mapper = MockMapper(self.yorm_path)
        self.yorm_mapper.store(self)
        self.yorm_mapper.auto = True

    def __repr__(self):
        return "<sample {}>".format(id(self))


@map_attr(abc=Integer)
class SampleDictionary(Dictionary):

    """Sample dictionary container."""


@map_attr(all=String)
class StringList(List):

    """Sample list container."""

    yorm_attrs = {'all': String}


class UnknownList(List):

    """Sample list container."""


# tests #######################################################################


class TestMappable:

    """Unit tests for the `Mappable` class."""

    def setup_method(self, method):
        """Create an mappable instance for tests."""
        self.sample = SampleMappable()

    def test_init(self):
        """Verify files are created after initialized."""
        text = self.sample.yorm_mapper.read()
        assert """
        var1: ''
        var2: 0
        var3: false
        """.strip().replace("        ", "") + '\n' == text

    def test_set(self):
        """Verify the file is written to after setting an attribute."""
        self.sample.var1 = "abc123"
        self.sample.var2 = 1
        self.sample.var3 = True
        text = self.sample.yorm_mapper.read()
        assert """
        var1: abc123
        var2: 1
        var3: true
        """.strip().replace("        ", "") + '\n' == text

    def test_set_converted(self):
        """Verify conversion occurs when setting attributes."""
        self.sample.var1 = 42
        self.sample.var2 = "1"
        self.sample.var3 = 'off'
        text = self.sample.yorm_mapper.read()
        assert """
        var1: '42'
        var2: 1
        var3: false
        """.strip().replace("        ", "") + '\n' == text

    def test_set_error(self):
        """Verify an exception is raised when a value cannot be converted."""
        with pytest.raises(ValueError):
            self.sample.var2 = "abc"

    def test_get(self):
        """Verify the file is read from before getting an attribute."""
        text = """
        var1: def456
        var2: 42
        var3: off
        """.strip().replace("        ", "") + '\n'
        self.sample.yorm_mapper.write(text)
        assert"def456" == self.sample.var1
        assert 42 == self.sample.var2
        assert False is self.sample.var3

    def test_error_invalid_yaml(self):
        """Verify an exception is raised on invalid YAML."""
        text = """
        invalid: -
        """.strip().replace("        ", "") + '\n'
        self.sample.yorm_mapper.write(text)
        with pytest.raises(ValueError):
            print(self.sample.var1)

    def test_error_unexpected_yaml(self):
        """Verify an exception is raised on unexpected YAML."""
        text = """
        not a dictionary
        """.strip().replace("        ", "") + '\n'
        self.sample.yorm_mapper.write(text)
        with pytest.raises(ValueError):
            print(self.sample.var1)

    def test_context_manager(self):
        """Verify the context manager delays write."""
        with self.sample:
            self.sample.var1 = "abc123"

            text = self.sample.yorm_mapper.read()
            assert """
            var1: ''
            var2: 0
            var3: false
            """.strip().replace("            ", "") + '\n' == text

        text = self.sample.yorm_mapper.read()
        assert """
        var1: abc123
        var2: 0
        var3: false
        """.strip().replace("        ", "") + '\n' == text

    def test_new(self):
        """Verify new attributes are added to the object."""
        text = """
        new: 42
        """.strip().replace("        ", "") + '\n'
        self.sample.yorm_mapper.write(text)
        assert 42 == self.sample.new

    def test_new_unknown(self):
        """Verify an exception is raised on new attributes w/ unknown types"""
        text = """
        new: !!timestamp 2001-12-15T02:59:43.1Z
        """.strip().replace("        ", "") + '\n'
        self.sample.yorm_mapper.write(text)
        with pytest.raises(ValueError):
            print(self.sample.var1)


class TestConverter:

    """Unit tests for the `Converter` class."""

    def test_not_implemented(self):
        """Verify `Converter` cannot be used directly."""
        with pytest.raises(NotImplementedError):
            Converter.to_value(None)  # pylint: disable=E1120
        with pytest.raises(NotImplementedError):
            Converter.to_data(None)  # pylint: disable=E1120


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
        assert None == UnknownList.item_type

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
