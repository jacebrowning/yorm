#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201

"""Unit tests for the `base` module."""

import pytest
import logging

from yorm.base import Mappable, Converter
from yorm.mapper import Mapper
from yorm.standard import String, Integer, Boolean


class MockMapper(Mapper):

    """Mapped file with stubbed file IO."""

    def __init__(self, path):
        super().__init__(path)
        self._mock_file = None

    def read(self):
        text = self._mock_file
        logging.debug("mock read:\n%s", text.strip())
        return text

    def write(self, text):
        logging.debug("mock write:\n%s", text.strip())
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


if __name__ == '__main__':
    pytest.main()
