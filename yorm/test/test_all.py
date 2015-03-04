#!/usr/bin/env python
# pylint:disable=R0201

"""Integration tests for the `yorm` package."""

import time
import logging

import pytest

from yorm import sync, attr, Converter
from yorm.container import Dictionary, List
from yorm.standard import Object, String, Integer, Float, Boolean
from yorm.extended import Markdown

integration = pytest.mark.integration


# custom converters ###########################################################


class Level(Converter):

    """Sample custom attribute."""

    @classmethod
    def to_value(cls, obj):
        if obj:
            if isinstance(obj, str):
                return obj
            else:
                return str(obj)
        else:
            return ""

    @classmethod
    def to_data(cls, obj):
        value = cls.to_value(obj)
        count = value.split('.')
        if count == 0:
            return int(value)
        elif count == 1:
            return float(value)
        else:
            return value


class EmptyDictionary(Dictionary):

    """Sample dictionary container."""


@attr(key=String)
class SingleKeyDictionary(Dictionary):

    """Sample dictionary container."""


@attr(all=Integer)
class IntegerList(List):

    """Sample list container."""


@attr(status=Boolean, label=String)
class StatusDictionary(Dictionary):

    """Sample dictionary container."""


@attr(all=StatusDictionary)
class StatusDictionaryList(List):

    """Sample list container."""


# sample classes ##############################################################


class SampleStandard:

    """Sample class using standard attribute types."""

    def __init__(self):
        # https://docs.python.org/3.4/library/json.html#json.JSONDecoder
        self.object = {}
        self.array = []
        self.string = ""
        self.number_int = 0
        self.number_real = 0.0
        self.true = True
        self.false = False
        self.null = None

    def __repr__(self):
        return "<standard {}>".format(id(self))


class SampleNested:

    """Sample class using nested attribute types."""

    def __init__(self):
        self.count = 0
        self.results = []

    def __repr__(self):
        return "<nested {}>".format(id(self))


@attr(object=EmptyDictionary, array=IntegerList, string=String)
@attr(number_int=Integer, number_real=Float)
@attr(true=Boolean, false=Boolean)
@sync("path/to/{self.category}/{self.name}.yml")
class SampleStandardDecorated:

    """Sample class using standard attribute types."""

    def __init__(self, name, category='default'):
        self.name = name
        self.category = category
        # https://docs.python.org/3.4/library/json.html#json.JSONDecoder
        self.object = {}
        self.array = []
        self.string = ""
        self.number_int = 0
        self.number_real = 0.0
        self.true = True
        self.false = False
        self.null = None

    def __repr__(self):
        return "<decorated {}>".format(id(self))


@attr(string=String, number_real=Float)
@sync("sample.yml", auto=False)
class SampleDecoratedNoAuto:

    """Sample class with automatic storage turned off."""

    def __init__(self):
        self.string = ""
        self.number_real = 0.0

    def __repr__(self):
        return "<no auto {}>".format(id(self))


@attr(string=String, number_real=Float)
class SampleDecoratedNoPath:

    """Sample class with a manually mapped path."""

    def __init__(self):
        self.string = ""
        self.number_real = 0.0

    def __repr__(self):
        return "<no path {}>".format(id(self))


@sync("sample.yml")
class SampleEmptyDecorated:

    """Sample class using standard attribute types."""

    def __repr__(self):
        return "<empty {}>".format(id(self))


class SampleExtended:

    """Sample class using extended attribute types."""

    def __init__(self):
        self.text = ""

    def __repr__(self):
        return "<extended {}>".format(id(self))


@sync("path/to/directory/{UUID}.yml", attrs={'level': Level})
class SampleCustomDecorated:

    """Sample class using custom attribute types."""

    def __init__(self, name):
        self.name = name
        self.level = '1.0'

    def __repr__(self):
        return "<custom {}>".format(id(self))


# tests #######################################################################


def refresh_file_modification_times(seconds=1.1):
    """Sleep to allow file modification times to refresh."""
    logging.info("delaying for %s second%s...", seconds,
                 "" if seconds == 1 else "s")
    time.sleep(seconds)


def test_imports():
    """Verify the package namespace is correct."""
    # pylint: disable=W0404,W0612,W0621

    import yorm

    # Constants
    from yorm import UUID  # filename placeholder

    # Classes
    from yorm import Mappable  # base class for mapped objects
    from yorm import Converter  # base class for converters
    from yorm.standard import String  # and others
    from yorm.extended import Markdown  # and others
    from yorm.container import List  # and others

    # Decorators
    from yorm import sync  # enables mapping on a class's instance objects
    from yorm import sync_instances  # alias for the class decorator
    from yorm import attr  # alternate API to identify mapped attributes

    # Functions
    from yorm import sync  # enables mapping on an instance object
    from yorm import sync_object  # alias for the mapping function
    from yorm import update  # fetch (if necessary) and store a mapped object
    from yorm import update_object  # fetch (optional force) a mapped object
    from yorm import update_file  # store a mapped object


@integration
class TestStandard:

    """Integration tests for standard attribute types."""

    def test_decorator(self, tmpdir):
        """Verify standard attribute types dump/load correctly (decorator)."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        assert "path/to/default/sample.yml" == sample.yorm_path

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
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
        array:
        - 0
        - 1
        - 2
        'false': true
        number_int: 42
        number_real: 4.2
        object:
          key2: value
        string: Hello, world!
        'true': false
        """.strip().replace("        ", "") + '\n' == text

        # change file values
        refresh_file_modification_times()
        text = """
        array: [4, 5, 6]
        'false': null
        number_int: 42
        number_real: '4.2'
        object: {'status': false}
        string: "abc"
        'true': null
        """.strip().replace("        ", "") + '\n'
        with open(sample.yorm_path, 'w') as stream:
            stream.write(text)

        # check object values
        assert {'key2': "",
                'status': False} == sample.object
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
        attrs = {'object': SingleKeyDictionary,
                 'array': IntegerList,
                 'string': String,
                 'number_int': Integer,
                 'number_real': Float,
                 'true': Boolean,
                 'false': Boolean}
        sample = sync(_sample, "path/to/directory/sample.yml", attrs)
        assert "path/to/directory/sample.yml" == sample.yorm_path

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
        sample.array = [1, 2, 3]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.true = None
        sample.false = 1

        # check file values
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
        array:
        - 1
        - 2
        - 3
        'false': true
        number_int: 42
        number_real: 4.2
        object:
          key: ''
          key2: value
        string: Hello, world!
        'true': false
        """.strip().replace("        ", "") + '\n' == text

    def test_with(self, tmpdir):
        """Verify standard attribute types dump/load correctly (with)."""
        tmpdir.chdir()
        _sample = SampleStandard()
        attrs = {'string': String,
                 'number_real': Float}
        sample = sync(_sample, "sample.yml", attrs, auto=False)

        # change object values
        with sample:
            sample.string = "abc"
            sample.number_real = 4.2

            # check for unchanged file values
            with open(sample.yorm_path, 'r') as stream:
                text = stream.read()
            assert "" == text

            # check for changed file values
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
        number_real: 4.2
        string: abc
        """.strip().replace("        ", "") + '\n' == text

    def test_no_auto(self, tmpdir):
        """Verify standard attribute types dump/load correctly (auto)."""
        tmpdir.chdir()
        sample = SampleDecoratedNoAuto()

        # change object values
        sample.string = "abc"
        sample.number_real = 4.2

        # check for unchanged file values
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert "" == text

        # store value
        sample.yorm_mapper.store(sample, sample.yorm_attrs)
        sample.yorm_mapper.auto = True

        # check for changed file values
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
        number_real: 4.2
        string: abc
        """.strip().replace("        ", "") + '\n' == text

    def test_no_path(self, tmpdir):
        """Verify standard attribute types dump/load correctly (path)."""
        tmpdir.chdir()
        sample = sync(SampleDecoratedNoPath(), "sample.yml")

        # change object values
        sample.string = "abc"
        sample.number_real = 4.2

        # check for changed file values
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
        number_real: 4.2
        string: abc
        """.strip().replace("        ", "") + '\n' == text


@integration
class TestContainers:

    """Integration tests for attribute containers."""

    def test_nesting(self, tmpdir):
        """Verify standard attribute types can be nested."""
        tmpdir.chdir()
        _sample = SampleNested()
        attrs = {'count': Integer,
                 'results': StatusDictionaryList}
        sample = sync(_sample, "sample.yml", attrs)

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
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
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
        """.strip().replace("        ", "") + '\n' == text

        # change file values
        refresh_file_modification_times()
        text = """
        count: 3
        other: 4.2
        results:
        - label: abc
        - label: null
          status: false
        - status: true
        """.strip().replace("        ", "") + '\n'
        with open(sample.yorm_path, 'w') as stream:
            stream.write(text)

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
        text = """
        object: {'key': 'value'}
        array: [1, '2', '3.0']
        """.strip().replace("        ", "") + '\n'
        with open(sample.yorm_path, 'w') as stream:
            stream.write(text)

        # (a mapped attribute must be read first to trigger retrieving)
        sample.yorm_mapper.fetch(sample, sample.yorm_attrs)

        # check object values
        assert {'key': 'value'} == sample.object
        assert [1, '2', '3.0'] == sample.array

        # check object types
        assert Object == sample.yorm_attrs['object']
        assert Object == sample.yorm_attrs['array']

        # change object values
        sample.object = None  # pylint: disable=W0201
        sample.array = "abc"  # pylint: disable=W0201

        # check file values
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
        array: abc
        object: null
        """.strip().replace("        ", "") + '\n' == text


@integration
class TestExtended:

    """Integration tests for extended attribute types."""

    def test_function(self, tmpdir):
        """Verify extended attribute types dump/load correctly."""
        tmpdir.chdir()
        _sample = SampleExtended()
        attrs = {'text': Markdown}
        sample = sync(_sample, "path/to/directory/sample.yml", attrs)

        # check defaults
        assert "" == sample.text

        # change object values
        refresh_file_modification_times()
        sample.text = """
        This is the first sentence. This is the second sentence.
        This is the third sentence.
        """.strip().replace("        ", "")

        # check file values
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
        text: |
          This is the first sentence.
          This is the second sentence.
          This is the third sentence.
        """.strip().replace("        ", "") + '\n' == text

        # change file values
        refresh_file_modification_times()
        text = """
        text: |
          This is a
          sentence.
        """.strip().replace("        ", "") + '\n'
        with open(sample.yorm_path, 'w') as stream:
            stream.write(text)

        # check object values
        assert "This is a sentence." == sample.text


@integration
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
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
        level: 1.2.3
        """.strip().replace("        ", "") + '\n' == text

        # change file values
        refresh_file_modification_times()
        text = """
        level: 1
        """.strip().replace("        ", "") + '\n'
        with open(sample.yorm_path, 'w') as stream:
            stream.write(text)

        # check object values
        assert '1' == sample.level


@integration
class TestInit:

    """Integration tests for initializing mapped classes."""

    def test_fetch_from_existing(self, tmpdir):
        """Verify attributes are updated from an existing file."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        sample2 = SampleStandardDecorated('sample')
        assert sample2.yorm_path == sample.yorm_path

        refresh_file_modification_times()

        logging.info("changing values in object 1...")
        sample.object = {'key2': 'value'}
        sample.array = [0, 1, 2]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.true = True
        sample.false = False

        logging.info("reading changed values in object 2...")
        assert 'value' == sample2.object.get('key2')
        assert [0, 1, 2] == sample2.array
        assert "Hello, world!" == sample2.string
        assert 42 == sample2.number_int
        assert 4.2 == sample2.number_real
        assert True is sample2.true
        assert False is sample2.false


@integration
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


if __name__ == '__main__':
    pytest.main()
