#!/usr/bin/env python
# pylint:disable=R0201

"""Integration tests for the `yorm.settings.fake` option."""

import os
import pytest
from unittest.mock import patch

import yorm

from . import strip


@yorm.attr(value=yorm.standard.Integer)
@yorm.sync("path/to/{self.name}.yml")
class Sample:

    """Sample class for fake mapping."""

    def __init__(self, name):
        self.name = name
        self.value = 0


@patch('yorm.settings.fake', True)
class TestFake:

    """Integration tests with `yorm.fake` enabled."""

    def test_fake(self, tmpdir):
        """Verify no file is created with fake enabled."""
        tmpdir.chdir()
        sample = Sample('sample')

        # ensure no file is created
        assert "path/to/sample.yml" == sample.yorm_path
        assert not os.path.exists(sample.yorm_path)

        # change object values
        sample.value = 42

        # check fake file
        assert strip("""
        value: 42
        """) == sample.yorm_mapper.fake

        # ensure no file is created
        assert not os.path.exists(sample.yorm_path)

        # change fake file
        sample.yorm_mapper.fake = "value2: abc\n"

        # check object values
        assert "abc" == sample.value2

        # ensure no file is created
        assert not os.path.exists(sample.yorm_path)

    def test_modified(self, tmpdir):
        """Verify fake file modifications are correct."""
        tmpdir.chdir()
        sample = Sample('sample')

        assert False is sample.yorm_mapper.modified
        assert 0 == sample.value

        sample.yorm_mapper.fake = "value: 42\n"

        assert True is sample.yorm_mapper.modified
        assert 42 == sample.value
        assert False is sample.yorm_mapper.modified


class TestReal:

    """Integration tests with `yorm.fake` disabled."""

    def test_error_when_real(self, tmpdir):
        """Verify it is an error to use fake file IO with fake disabled."""
        tmpdir.chdir()
        sample = Sample('sample')

        with pytest.raises(AttributeError):
            print(sample.yorm_mapper.fake)

        with pytest.raises(AttributeError):
            sample.yorm_mapper.fake = None


if __name__ == '__main__':
    pytest.main()
