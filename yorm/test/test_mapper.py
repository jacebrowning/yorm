#!/usr/bin/env python
# pylint: disable=R,C

"""Unit tests for the `mapper` module."""

import os
import pytest
from unittest.mock import patch, Mock

from yorm import exceptions
from yorm.mapper import Helper, Mapper
from yorm.converters import Integer


@patch('yorm.settings.fake', True)
class TestHelperFake:

    """Unit tests for fake mappings using the `Helper` class."""

    def test_create(self):
        """Verify fake files can be created."""
        mapper = Helper("fake/path/to/file")
        mapper.create(Mock())

        assert False is os.path.exists(mapper.path)

    def test_delete(self):
        """Verify fake files can be deleted."""
        mapper = Helper("fake/path/to/file")
        mapper.create(None)
        mapper.delete()

        assert False is os.path.exists(mapper.path)

    def test_create_after_delete(self):
        mapper = Helper("fake/path/to/file")
        mapper.create(None)
        mapper.delete()

        assert False is mapper.exists
        assert True is mapper.deleted

        mapper.create(None)

        assert True is mapper.exists
        assert False is mapper.deleted

    def test_modified(self):
        """Verify fake files can be modified."""
        mapper = Helper("fake/path/to/file")

        assert True is mapper.modified

        mapper.create(None)

        assert True is mapper.modified

        mapper.modified = False

        assert False is mapper.modified

        mapper.modified = True

        assert True is mapper.modified


class TestHelperReal:

    """Unit tests for real mappings using the `Helper` class."""

    def test_create(self, tmpdir):
        """Verify files can be created."""
        tmpdir.chdir()
        mapper = Helper("real/path/to/file")
        mapper.create(None)

        assert True is os.path.isfile(mapper.path)
        assert True is mapper.exists
        assert False is mapper.deleted

    def test_create_twice(self, tmpdir):
        """Verify the second creation is ignored."""
        tmpdir.chdir()
        mapper = Helper("real/path/to/file")
        mapper.create(None)
        mapper.create(None)

        assert True is os.path.isfile(mapper.path)
        assert True is mapper.exists
        assert False is mapper.deleted

    def test_delete(self, tmpdir):
        """Verify files can be deleted."""
        tmpdir.chdir()
        mapper = Helper("real/path/to/file")
        mapper.create(None)
        mapper.delete()

        assert False is os.path.exists(mapper.path)
        assert False is mapper.exists
        assert True is mapper.deleted
        with pytest.raises(exceptions.FileDeletedError):
            mapper.fetch(None, None)

    def test_delete_twice(self, tmpdir):
        """Verify the second deletion is ignored."""
        tmpdir.chdir()
        mapper = Helper("real/path/to/file")
        mapper.delete()

        assert False is os.path.exists(mapper.path)
        assert False is mapper.exists
        assert True is mapper.deleted

    def test_modified(self, tmpdir):
        """Verify files track modifications."""
        tmpdir.chdir()
        mapper = Helper("real/path/to/file")

        assert True is mapper.modified

        mapper.create(None)

        assert True is mapper.modified

        mapper.modified = False

        assert False is mapper.modified

        mapper.modified = True

        assert True is mapper.modified

    def test_modified_deleted(self):
        """Verify a deleted file is always modified."""
        mapper = Helper("fake/path/to/file")

        assert True is mapper.modified


class TestMapper:

    """Unit tests for the `Mapper` class."""

    class MyObject:
        foo = 1

    def test_store_ignores_auto_off(self, tmpdir):
        tmpdir.chdir()
        obj = self.MyObject()
        attrs = {'number': Integer}
        mapper = Mapper(obj, "real/path/to/file", attrs, auto=False)

        assert "" == mapper.text
        assert False is mapper.auto

        mapper.create()

        assert "" == mapper.text
        assert False is mapper.auto

        mapper.store()

        assert "number: 0\n" == mapper.text
        assert False is mapper.auto

    def test_missing_attributes_added(self):
        obj = self.MyObject()
        path = "mock/path"
        attrs = {'bar': Integer, 'qux': Integer}
        mapper = Mapper(obj, path, attrs)
        mapper.create()
        mapper.fetch()

        assert 1 == obj.foo
        assert 0 == obj.bar
        assert 0 == obj.qux


if __name__ == '__main__':
    pytest.main()
