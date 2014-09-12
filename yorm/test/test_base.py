#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201

"""Unit tests for the `base` module."""

import pytest

from yorm import Mappable
from yorm.standard import String, Integer, Boolean


class MockSample(Mappable):

    """Sample mappable class with mocked file IO."""

    __path__ = "mock/path/to/sample.yml"
    __mapping__ = {'var1': String,
                   'var2': Integer,
                   'var3': Boolean}

    mock_file = ""

    def __init__(self):
        super().__init__()
        self.var1 = ""
        self.var2 = 0
        self.var3 = False

    def _read(self, path):
        return self.mock_file

    def _write(self, text, path):
        self.mock_file = text


class TestMappable:

    """Unit tests for the `Mappable` class."""

    def setup_method(self, method):
        """Create an mappable instance for tests."""
        self.sample = MockSample()

    def test_init(self):
        """Verify files are created after initialized."""
        assert self.sample.mock_file == """
        var1: ''
        var2: 0
        var3: false
        """.strip().replace("        ", "") + '\n'

    def test_save(self):
        """Verify the file is written to after setting an attribute."""
        self.sample.var1 = "abc123"
        assert self.sample.mock_file == """
        var1: abc123
        var2: 0
        var3: false
        """.strip().replace("        ", "") + '\n'

    def test_load(self):
        """Verify the file is read from before getting an attribute."""
        self.sample.mock_file = """
        var1: def456
        var2: 42
        var3: true
        """.strip().replace("        ", "") + '\n'
        assert self.sample.var1 == "def456"
        assert self.sample.var2 == 42
        assert self.sample.var3 is True

    def test_error_invalid_yaml(self):
        """Verify an exception is raised on invalid YAML."""
        self.sample.mock_file = """
        invalid: -
        """.strip().replace("        ", "") + '\n'
        with pytest.raises(ValueError):
            print(self.sample.var1)

    def test_error_unexpected_yaml(self):
        """Verify an exception is raised on unexpected YAML."""
        self.sample.mock_file = """
        not a dictionary
        """.strip().replace("        ", "") + '\n'
        with pytest.raises(ValueError):
            print(self.sample.var1)


if __name__ == '__main__':
    pytest.main()
