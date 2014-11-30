#!/usr/bin/env python
# pylint:disable=R0201

"""Integration tests for the `common` module."""

import os
import pytest

from yorm import common


def test_file_creation(tmpdir):
    """Verify a file can be created in an existing directory."""
    tmpdir.chdir()

    path = os.path.join('.', 'file.ext')

    common.touch(path)
    assert os.path.isfile(path)

    common.touch(path)  # second call is ignored
    assert os.path.isfile(path)


def test_file_creation_nested(tmpdir):
    """Verify a file can be created in a new directory."""
    tmpdir.chdir()

    dirpath = os.path.join('path', 'to', 'directory')
    path = os.path.join(dirpath, 'file.ext')

    common.touch(path)
    assert os.path.isfile(path)


def test_file_deletion(tmpdir):
    """Verify a file can be deleted."""
    tmpdir.chdir()

    path = os.path.join('.', 'file.ext')

    common.touch(path)
    assert os.path.isfile(path)

    common.delete(path)
    assert not os.path.isfile(path)

    common.delete(path)  # second call is ignored
    assert not os.path.isfile(path)


def test_directory_deletion(tmpdir):
    """Verify a directory can be deleted."""
    tmpdir.chdir()

    dirpath = os.path.join('path', 'to', 'directory')
    path = os.path.join(dirpath, 'file.ext')

    common.touch(path)
    assert os.path.isdir(dirpath)

    common.delete(dirpath)
    assert not os.path.isdir(dirpath)

    common.delete(dirpath)  # second call is ignored
    assert not os.path.isdir(dirpath)


if __name__ == '__main__':
    pytest.main()
