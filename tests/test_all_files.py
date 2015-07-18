# pylint:disable=R,C

"""Integration tests for file IO."""

import logging

import pytest

from yorm.common import write_text

from . import refresh_file_modification_times
from .samples import *  # pylint: disable=W0401,W0614


class TestCreate:

    """Integration tests for creating mapped classes."""

    def test_fetch_from_existing(self, tmpdir):
        """Verify attributes are updated from an existing file."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        sample2 = SampleStandardDecorated('sample')
        assert sample2.yorm_mapper.path == sample.yorm_mapper.path

        refresh_file_modification_times()

        logging.info("changing values in object 1...")
        sample.array = [0, 1, 2]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.true = True
        sample.false = False

        logging.info("reading changed values in object 2...")
        assert [0, 1, 2] == sample2.array
        assert "Hello, world!" == sample2.string
        assert 42 == sample2.number_int
        assert 4.2 == sample2.number_real
        assert True is sample2.true
        assert False is sample2.false


class TestDelete:

    """Integration tests for deleting files."""

    def test_read(self, tmpdir):
        """Verify a deleted file cannot be read from."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        sample.yorm_mapper.delete()

        with pytest.raises(FileNotFoundError):
            print(sample.string)

        with pytest.raises(FileNotFoundError):
            sample.string = "def456"

    def test_write(self, tmpdir):
        """Verify a deleted file cannot be written to."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        sample.yorm_mapper.delete()

        with pytest.raises(FileNotFoundError):
            sample.string = "def456"

    def test_multiple(self, tmpdir):
        """Verify a deleted file can be deleted again."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        sample.yorm_mapper.delete()
        sample.yorm_mapper.delete()


class TestUpdate:

    """Integration tests for updating files/object."""

    def test_automatic_store_after_first_modification(self, tmpdir):
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        assert "number_int: 0\n" in sample.yorm_mapper.text

        sample.number_int = 42
        assert "number_int: 42\n" in sample.yorm_mapper.text

        sample.yorm_mapper.text = "number_int: true\n"
        assert 1 is sample.number_int
        assert "number_int: 1\n" in sample.yorm_mapper.text

    def test_automatic_store_after_first_modification_on_list(self, tmpdir):
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        assert "array: []\n" in sample.yorm_mapper.text

        sample.array.append(42)
        assert "array:\n- 42\n" in sample.yorm_mapper.text

        sample.yorm_mapper.text = "array: [true]\n"
        try:
            iter(sample)
        except AttributeError:
            pass
        assert "array:\n- 1\n" in sample.yorm_mapper.text
