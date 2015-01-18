#!/usr/bin/env python
# pylint: disable=R0201

"""Unit tests for the `mapper` module."""

import os
import pytest
from unittest.mock import patch, Mock

from yorm import mapper


@patch('yorm.settings.fake', True)
class TestFake:

    """Unit tests for fake mappings."""

    def test_create(self):
        """Verify fake files can be created."""
        mapped = mapper.Mapper("fake/path/to/file")
        mapped.create(Mock())

        assert not os.path.exists(mapped.path)

    def test_delete(self):
        """Verify fake files can be deleted."""
        mapped = mapper.Mapper("fake/path/to/file")
        mapped.create(None)
        mapped.delete()

        assert not os.path.exists(mapped.path)


class TestReal:

    """Unit tests for real mappings."""

    def test_create(self, tmpdir):
        """Verify files can be created."""
        tmpdir.chdir()
        mapped = mapper.Mapper("real/path/to/file")
        mapped.create(None)

        assert os.path.isfile(mapped.path)

    def test_create_exists(self, tmpdir):
        """Verify files are only created if they don't exist."""
        tmpdir.chdir()
        mapped = mapper.Mapper("real/path/to/file")
        with patch('os.path.isfile', Mock(return_value=True)):
            mapped.create(None)

        assert not os.path.isfile(mapped.path)

    def test_delete(self, tmpdir):
        """Verify files can be deleted."""
        tmpdir.chdir()
        mapped = mapper.Mapper("real/path/to/file")
        mapped.create(None)
        mapped.delete()

        assert not os.path.exists(mapped.path)


if __name__ == '__main__':
    pytest.main()
