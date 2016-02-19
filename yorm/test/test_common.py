# pylint: disable=missing-docstring,expression-not-assigned,unused-variable

import os

import pytest
from expecter import expect

from yorm import common


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
        common.touch(new_path)
        expect(os.path.exists(new_path)).is_true()

    def it_can_be_called_twice(new_path):
        common.touch(new_path)
        common.touch(new_path)
        expect(os.path.exists(new_path)).is_true()

    def it_creates_missing_directories(new_path_in_directory):
        common.touch(new_path_in_directory)
        expect(os.path.exists(new_path_in_directory)).is_true()


def describe_delete():

    @pytest.fixture
    def existing_path(tmpdir):
        tmpdir.chdir()
        path = "path/to/file.ext"
        os.system("touch {}".format(path))
        return path

    @pytest.fixture
    def existing_dirpath(tmpdir):
        tmpdir.chdir()
        dirpath = "path/to/directory"
        os.system("mkdir -p {}".format(dirpath))
        return dirpath

    def it_deletes_existing_files(existing_path):
        common.delete(existing_path)
        expect(os.path.exists(existing_path)).is_false()

    def it_ignores_missing_files():
        common.delete("path/to/non/file")

    def it_deletes_directories(existing_dirpath):
        common.delete(existing_dirpath)
        expect(os.path.exists(existing_dirpath)).is_false()
