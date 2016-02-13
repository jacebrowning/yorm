"""Integration tests for the `yorm.settings.fake` option."""
# pylint: disable=missing-docstring,no-self-use,no-member,misplaced-comparison-constant


import os
from unittest.mock import patch

import yorm

from . import strip


# CLASSES ######################################################################


@yorm.attr(value=yorm.types.standard.Integer)
@yorm.sync("path/to/{self.name}.yml")
class Sample:
    """Sample class for fake mapping."""

    def __init__(self, name):
        self.name = name
        self.value = 0

    def __repr__(self):
        return "<sample {}>".format(id(self))


# TESTS ########################################################################


@patch('yorm.settings.fake', True)
class TestFake:
    """Integration tests with `yorm.settings.fake` enabled."""

    def test_no_file_create_when_fake(self, tmpdir):
        tmpdir.chdir()
        sample = Sample('sample')

        # ensure no file is created
        assert "path/to/sample.yml" == sample.__mapper__.path
        assert not os.path.exists(sample.__mapper__.path)

        # change object values
        sample.value = 42

        # check fake file
        assert strip("""
        value: 42
        """) == sample.__mapper__.text

        # ensure no file is created
        assert not os.path.exists(sample.__mapper__.path)

        # change fake file
        sample.__mapper__.text = "value: 0\n"

        # check object values
        assert 0 == sample.value

        # ensure no file is created
        assert not os.path.exists(sample.__mapper__.path)

    def test_fake_changes_indicate_modified(self, tmpdir):
        tmpdir.chdir()
        sample = Sample('sample')

        assert False is sample.__mapper__.modified
        assert 0 == sample.value

        sample.__mapper__.text = "value: 42\n"

        assert True is sample.__mapper__.modified
        assert 42 == sample.value
        assert False is sample.__mapper__.modified


class TestReal:
    """Integration tests with `yorm.settings.fake` disabled."""

    def test_setting_text_updates_attributes(self, tmpdir):
        tmpdir.chdir()
        sample = Sample('sample')

        sample.__mapper__.text = "value: 42"

        assert 42 == sample.value

    def test_setting_attributes_update_text(self, tmpdir):
        tmpdir.chdir()
        sample = Sample('sample')

        sample.value = 42

        assert strip("""
        value: 42
        """) == sample.__mapper__.text
