#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201

"""Unit tests for the `base` module."""

import pytest
from unittest.mock import patch
import logging

from yorm.base import Mappable, Mapper
from yorm.standard import String, Integer, Boolean


class MockMapper(Mapper):

    """Mapped file with stubbed file IO."""

    _mock_file = ""

    @staticmethod
    def read(obj):
        text = MockMapper._mock_file
        logging.debug("mock read:\n{}".format(text.strip()))
        return text

    @staticmethod
    def write(obj, text):
        logging.debug("mock write:\n{}".format(text.strip()))
        MockMapper._mock_file = text


class Sample(Mappable):

    """Sample mappable class with hard-coded settings."""

    yorm_path = "mock/path/to/sample.yml"
    yorm_attrs = {'var1': String,
                  'var2': Integer,
                  'var3': Boolean}

    yorm_mapper = MockMapper()

    def __init__(self):
        logging.debug("initializing sample...")
        self.var1 = ""
        self.var2 = 0
        self.var3 = False

        self.auto = True
        self.yorm_mapper.store(self)
        logging.debug("sample initialized")


class TestMappable:

    """Unit tests for the `Mappable` class."""

    def setup_method(self, method):
        """Create an mappable instance for tests."""
        self.sample = Sample()

    def test_init(self):
        """Verify files are created after initialized."""
        text = self.sample.yorm_mapper.read(self.sample)
        assert text == """
        var1: ''
        var2: 0
        var3: false
        """.strip().replace("        ", "") + '\n'

    def test_save(self):
        """Verify the file is written to after setting an attribute."""
        self.sample.var1 = "abc123"
        self.sample.var2 = 1
        self.sample.var3 = True
        text = self.sample.yorm_mapper.read(self.sample)
        assert text == """
        var1: abc123
        var2: 1
        var3: true
        """.strip().replace("        ", "") + '\n'

    def test_load(self):
        """Verify the file is read from before getting an attribute."""
        text = """
        var1: def456
        var2: 42
        var3: off
        """.strip().replace("        ", "") + '\n'
        self.sample.yorm_mapper.write(self.sample, text)
        assert self.sample.var1 == "def456"
        assert self.sample.var2 == 42
        assert self.sample.var3 is False

    def test_error_invalid_yaml(self):
        """Verify an exception is raised on invalid YAML."""
        text = """
        invalid: -
        """.strip().replace("        ", "") + '\n'
        self.sample.yorm_mapper.write(self.sample, text)
        with pytest.raises(ValueError):
            print(self.sample.var1)

    def test_error_unexpected_yaml(self):
        """Verify an exception is raised on unexpected YAML."""
        text = """
        not a dictionary
        """.strip().replace("        ", "") + '\n'
        self.sample.yorm_mapper.write(self.sample, text)
        with pytest.raises(ValueError):
            print(self.sample.var1)


if __name__ == '__main__':
    pytest.main()
