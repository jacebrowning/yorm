"""Integration tests for the `yorm.settings.fake` option."""
# pylint: disable=missing-docstring,no-self-use


import os
from unittest.mock import patch

import yorm
from yorm.mapper import get_mapper

from . import strip


# classes ######################################################################


@yorm.attr(value=yorm.converters.standard.Integer)
@yorm.sync("path/to/{self.name}.yml")
class Sample:

    """Sample class for fake mapping."""

    def __init__(self, name):
        self.name = name
        self.value = 0

    def __repr__(self):
        return "<sample {}>".format(id(self))


# tests ########################################################################


@patch('yorm.settings.fake', True)
class TestFake:

    """Integration tests with `yorm.settings.fake` enabled."""

    def test_no_file_create_when_fake(self, tmpdir):
        tmpdir.chdir()
        sample = Sample('sample')

        # ensure no file is created
        assert "path/to/sample.yml" == get_mapper(sample).path
        assert not os.path.exists(get_mapper(sample).path)

        # change object values
        sample.value = 42

        # check fake file
        assert strip("""
        value: 42
        """) == get_mapper(sample).text

        # ensure no file is created
        assert not os.path.exists(get_mapper(sample).path)

        # change fake file
        get_mapper(sample).text = "value: 0\n"

        # check object values
        assert 0 == sample.value

        # ensure no file is created
        assert not os.path.exists(get_mapper(sample).path)

    def test_fake_changes_indicate_modified(self, tmpdir):
        tmpdir.chdir()
        sample = Sample('sample')

        assert False is get_mapper(sample).modified
        assert 0 == sample.value

        get_mapper(sample).text = "value: 42\n"

        assert True is get_mapper(sample).modified
        assert 42 == sample.value
        assert False is get_mapper(sample).modified


class TestReal:

    """Integration tests with `yorm.settings.fake` disabled."""

    def test_setting_text_updates_attributes(self, tmpdir):
        tmpdir.chdir()
        sample = Sample('sample')

        get_mapper(sample).text = "value: 42"

        assert 42 == sample.value

    def test_setting_attributes_update_text(self, tmpdir):
        tmpdir.chdir()
        sample = Sample('sample')

        sample.value = 42

        assert strip("""
        value: 42
        """) == get_mapper(sample).text
