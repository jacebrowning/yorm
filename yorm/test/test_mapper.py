#!/usr/bin/env python
# pylint: disable=R0201

"""Unit tests for the `mapper` module."""

import os
import pytest
from unittest.mock import patch, Mock

from yorm import mapper
from yorm.converters import Integer


@patch('yorm.settings.fake', True)
class TestHelperFake:

    """Unit tests for fake mappings using the `Helper` class."""

    def test_create(self):
        """Verify fake files can be created."""
        mapped = mapper.Helper("fake/path/to/file")
        mapped.create(Mock())

        assert not os.path.exists(mapped.path)

    def test_delete(self):
        """Verify fake files can be deleted."""
        mapped = mapper.Helper("fake/path/to/file")
        mapped.create(None)
        mapped.delete()

        assert not os.path.exists(mapped.path)

    def test_modified(self):
        """Verify fake files can be modified."""
        mapped = mapper.Helper("fake/path/to/file")
        assert mapped.modified

        mapped.create(None)
        assert mapped.modified

        mapped.modified = False
        assert not mapped.modified

        mapped.modified = True
        assert mapped.modified


class TestHelperReal:

    """Unit tests for real mappings using the `Helper` class."""

    def test_create(self, tmpdir):
        """Verify files can be created."""
        tmpdir.chdir()
        mapped = mapper.Helper("real/path/to/file")
        mapped.create(None)

        assert os.path.isfile(mapped.path)

    def test_create_twice(self, tmpdir):
        """Verify the second creation is ignored."""
        tmpdir.chdir()
        mapped = mapper.Helper("real/path/to/file")
        mapped.create(None)
        mapped.create(None)

        assert os.path.isfile(mapped.path)

    def test_delete(self, tmpdir):
        """Verify files can be deleted."""
        tmpdir.chdir()
        mapped = mapper.Helper("real/path/to/file")
        mapped.create(None)
        mapped.delete()

        assert not os.path.exists(mapped.path)

    def test_delete_twice(self, tmpdir):
        """Verify the second deletion is ignored."""
        tmpdir.chdir()
        mapped = mapper.Helper("real/path/to/file")
        mapped.delete()

        assert not os.path.exists(mapped.path)

    def test_modified(self, tmpdir):
        """Verify files track modifications."""
        tmpdir.chdir()
        mapped = mapper.Helper("real/path/to/file")
        assert mapped.modified

        mapped.create(None)
        assert mapped.modified

        mapped.modified = False
        assert not mapped.modified

        mapped.modified = True
        assert mapped.modified

    def test_modified_deleted(self):
        """Verify a deleted file is always modified."""
        mapped = mapper.Helper("fake/path/to/file")

        assert mapped.modified


class TestMapper:

    """Unit tests for the `Mapper` class."""

    def test_auto_off(self, tmpdir):
        """Verify storage is delayed with auto off."""
        tmpdir.chdir()
        attrs = {'number': Integer}
        mapped = mapper.Mapper(None, "real/path/to/file", attrs, auto=False)
        assert False is mapped.auto

        mapped.create()
        assert "" == mapped.text
        assert False is mapped.auto

        mapped.store()
        assert "" == mapped.text
        assert False is mapped.auto

        mapped.store(force=True)
        assert "number: 0\n" == mapped.text
        assert False is mapped.auto


if __name__ == '__main__':
    pytest.main()
