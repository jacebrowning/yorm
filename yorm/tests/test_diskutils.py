# pylint: disable=missing-docstring,expression-not-assigned,unused-variable

import os

import pytest
from expecter import expect

from yorm import diskutils


def describe_touch():

    @pytest.fixture
    def new_path(tmpdir):
        tmpdir.chdir()
        return os.path.join('.', 'file.ext')

    @pytest.fixture
    def new_path_in_directory():
        dirpath = os.path.join('path', 'to', 'directory')
        return os.path.join(dirpath, 'file.ext')

    def it_creates_files(new_path):
        diskutils.touch(new_path)
        expect(os.path.exists(new_path)).is_true()

    def it_can_be_called_twice(new_path):
        diskutils.touch(new_path)
        diskutils.touch(new_path)
        expect(os.path.exists(new_path)).is_true()

    def it_creates_missing_directories(new_path_in_directory):
        diskutils.touch(new_path_in_directory)
        expect(os.path.exists(new_path_in_directory)).is_true()


def describe_delete():

    @pytest.fixture
    def existing_path(tmpdir):
        tmpdir.chdir()
        path = "tmp/path/to/file.ext"
        os.makedirs(os.path.dirname(path))
        open(path, 'w').close()
        return path

    @pytest.fixture
    def existing_dirpath(tmpdir):
        tmpdir.chdir()
        dirpath = "tmp/path/to/directory"
        os.makedirs(dirpath)
        return dirpath

    def it_deletes_existing_files(existing_path):
        diskutils.delete(existing_path)
        expect(os.path.exists(existing_path)).is_false()

    def it_ignores_missing_files():
        diskutils.delete("tmp/path/to/non/file")

    def it_deletes_directories(existing_dirpath):
        diskutils.delete(existing_dirpath)
        expect(os.path.exists(existing_dirpath)).is_false()
