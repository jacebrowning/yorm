#!/usr/bin/env python
# pylint:disable=R0201,C0111

"""Integration tests for the package."""

import pytest

import yorm
from yorm.converters import Object, String, Integer, Float, Boolean
from yorm.converters import Markdown

from . import strip, refresh_file_modification_times
from .samples import *  # pylint: disable=W0401,W0614


class TestStandard:

    """Integration tests for standard attribute types."""

    @yorm.attr(status=yorm.converters.Boolean)
    class StatusDictionary(Dictionary):
        pass

    def test_decorator(self, tmpdir):
        """Verify standard attribute types dump/load correctly (decorator)."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        assert "path/to/default/sample.yml" == sample.yorm_mapper.path

        # check defaults
        assert {} == sample.object
        assert [] == sample.array
        assert "" == sample.string
        assert 0 == sample.number_int
        assert 0.0 == sample.number_real
        assert True is sample.true
        assert False is sample.false
        assert None is sample.null

        # change object values
        sample.object = {'key2': 'value'}
        sample.array = [0, 1, 2]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.true = False
        sample.false = True

        # check file values
        assert strip("""
        array:
        - 0
        - 1
        - 2
        'false': true
        number_int: 42
        number_real: 4.2
        object: {}
        string: Hello, world!
        'true': false
        """) == sample.yorm_mapper.text

        # change file values
        refresh_file_modification_times()
        sample.yorm_mapper.text = strip("""
        array: [4, 5, 6]
        'false': null
        number_int: 42
        number_real: '4.2'
        object: {'status': false}
        string: "abc"
        'true': null
        """)

        # check object values
        assert {'status': False} == sample.object
        assert [4, 5, 6] == sample.array
        assert "abc" == sample.string
        assert 42 == sample.number_int
        assert 4.2 == sample.number_real
        assert False is sample.true
        assert False is sample.false

    def test_function(self, tmpdir):
        """Verify standard attribute types dump/load correctly (function)."""
        tmpdir.chdir()
        _sample = SampleStandard()
        attrs = {'object': self.StatusDictionary,
                 'array': IntegerList,
                 'string': String,
                 'number_int': Integer,
                 'number_real': Float,
                 'true': Boolean,
                 'false': Boolean}
        sample = yorm.sync(_sample, "path/to/directory/sample.yml", attrs)
        assert "path/to/directory/sample.yml" == sample.yorm_mapper.path

        # check defaults
        assert {'status': False} == sample.object
        assert [] == sample.array
        assert "" == sample.string
        assert 0 == sample.number_int
        assert 0.0 == sample.number_real
        assert True is sample.true
        assert False is sample.false
        assert None is sample.null

        # change object values
        sample.object = {'key': 'value'}
        sample.array = [1, 2, 3]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.true = None
        sample.false = 1

        # check file values
        assert strip("""
        array:
        - 1
        - 2
        - 3
        'false': true
        number_int: 42
        number_real: 4.2
        object:
          status: false
        string: Hello, world!
        'true': false
        """) == sample.yorm_mapper.text

    def test_auto_off(self, tmpdir):
        """Verify file updates are disabled with auto off."""
        tmpdir.chdir()
        sample = SampleDecoratedAutoOff()

        # ensure the file does not exist
        assert False is sample.yorm_mapper.exists
        assert "" == sample.yorm_mapper.text

        # store value
        sample.string = "hello"

        # ensure the file still does not exist
        assert False is sample.yorm_mapper.exists
        assert "" == sample.yorm_mapper.text

        # enable auto and store value
        sample.yorm_mapper.auto = True
        sample.string = "world"

        # check for changed file values
        assert strip("""
        string: world
        """) == sample.yorm_mapper.text


class TestContainers:

    """Integration tests for attribute containers."""

    def test_nesting(self, tmpdir):
        """Verify standard attribute types can be nested."""
        tmpdir.chdir()
        _sample = SampleNested()
        attrs = {'count': Integer,
                 'results': StatusDictionaryList}
        sample = yorm.sync(_sample, "sample.yml", attrs)

        # check defaults
        assert 0 == sample.count
        assert [] == sample.results

        # change object values
        sample.count = 5
        sample.results = [{'status': False, 'label': "abc"},
                          {'status': None, 'label': None},
                          {'label': "def"},
                          {'status': True},
                          {}]

        # check file values
        assert strip("""
        count: 5
        results:
        - label: abc
          status: false
        - label: ''
          status: false
        - label: def
          status: false
        - label: ''
          status: true
        - label: ''
          status: false
        """) == sample.yorm_mapper.text

        # change file values
        refresh_file_modification_times()
        sample.yorm_mapper.text = strip("""
        count: 3
        other: 4.2
        results:
        - label: abc
        - label: null
          status: false
        - status: true
        """)

        # check object values
        assert 3 == sample.count
        assert 4.2 == sample.other
        assert [{'label': 'abc', 'status': False},
                {'label': '', 'status': False},
                {'label': '', 'status': True}] == sample.results

    def test_objects(self, tmpdir):
        """Verify containers are treated as objects when added."""
        tmpdir.chdir()
        sample = SampleEmptyDecorated()

        # change file values
        refresh_file_modification_times()
        sample.yorm_mapper.text = strip("""
        object: {'key': 'value'}
        array: [1, '2', '3.0']
        """)

        # (a mapped attribute must be read first to trigger retrieving)
        sample.yorm_mapper.fetch()

        # check object values
        assert {'key': 'value'} == sample.object
        assert [1, '2', '3.0'] == sample.array

        # check object types
        assert Object == sample.yorm_mapper.attrs['object']
        assert Object == sample.yorm_mapper.attrs['array']

        # change object values
        sample.object = None  # pylint: disable=W0201
        sample.array = "abc"  # pylint: disable=W0201

        # check file values
        assert strip("""
        array: abc
        object: null
        """) == sample.yorm_mapper.text


class TestExtended:

    """Integration tests for extended attribute types."""

    def test_function(self, tmpdir):
        """Verify extended attribute types dump/load correctly."""
        tmpdir.chdir()
        _sample = SampleExtended()
        attrs = {'text': Markdown}
        sample = yorm.sync(_sample, "path/to/directory/sample.yml", attrs)

        # check defaults
        assert "" == sample.text

        # change object values
        refresh_file_modification_times()
        sample.text = strip("""
        This is the first sentence. This is the second sentence.
        This is the third sentence.
        """)

        # check file values
        assert strip("""
        text: |
          This is the first sentence.
          This is the second sentence.
          This is the third sentence.
        """) == sample.yorm_mapper.text

        # change file values
        refresh_file_modification_times()
        sample.yorm_mapper.text = strip("""
        text: |
          This is a
          sentence.
        """)

        # check object values
        assert "This is a sentence." == sample.text


class TestCustom:

    """Integration tests for custom attribute types."""

    def test_decorator(self, tmpdir):
        """Verify custom attribute types dump/load correctly."""
        tmpdir.chdir()
        sample = SampleCustomDecorated('sample')

        # check defaults
        assert '1.0' == sample.level

        # change values
        sample.level = '1.2.3'

        # check file values
        assert strip("""
        level: 1.2.3
        """) == sample.yorm_mapper.text

        # change file values
        refresh_file_modification_times()
        sample.yorm_mapper.text = strip("""
        level: 1
        """)

        # check object values
        assert '1' == sample.level


if __name__ == '__main__':
    pytest.main()
