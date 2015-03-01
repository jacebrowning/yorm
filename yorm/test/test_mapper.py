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

    def test_modified(self):
        """Verify a fake file is always modified."""
        mapped = mapper.Mapper("fake/path/to/file")
        mapped.create(None)

        assert mapped.modified

        mapped.modified = False

        assert mapped.modified


class TestReal:

    """Unit tests for real mappings."""

    def test_create(self, tmpdir):
        """Verify files can be created."""
        tmpdir.chdir()
        mapped = mapper.Mapper("real/path/to/file")
        mapped.create(None)

        assert os.path.isfile(mapped.path)

    def test_create_twice(self, tmpdir):
        """Verify the second creation is ignored."""
        tmpdir.chdir()
        mapped = mapper.Mapper("real/path/to/file")
        mapped.create(None)
        mapped.create(None)

        assert os.path.isfile(mapped.path)

    def test_delete(self, tmpdir):
        """Verify files can be deleted."""
        tmpdir.chdir()
        mapped = mapper.Mapper("real/path/to/file")
        mapped.create(None)
        mapped.delete()

        assert not os.path.exists(mapped.path)

    def test_delete_twice(self, tmpdir):
        """Verify the second deletion is ignored."""
        tmpdir.chdir()
        mapped = mapper.Mapper("real/path/to/file")
        mapped.delete()

        assert not os.path.exists(mapped.path)

    def test_modified(self, tmpdir):
        """Verify files track modifications."""
        tmpdir.chdir()
        mapped = mapper.Mapper("real/path/to/file")
        mapped.create(None)

        assert not mapped.modified

        mapped.modified = True

        assert mapped.modified

    def test_modified_deleted(self):
        """Verify a deleted file is always modified."""
        mapped = mapper.Mapper("fake/path/to/file")

        assert mapped.modified


if __name__ == '__main__':
    pytest.main()
