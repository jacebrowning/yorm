#!/usr/bin/env python
# pylint:disable=R0201

"""Integration tests for the `yorm` package."""

import pytest

from yorm import store, store_instances, map_attr, Converter
from yorm.standard import Dictionary, List, String, Integer, Float, Boolean
from yorm.extended import Markdown

integration = pytest.mark.integration


# custom types ################################################################


class Level(Converter):

    """Sample custom attribute."""

    @staticmethod
    def to_value(obj):
        if obj:
            if isinstance(obj, str):
                return obj
            else:
                return str(obj)
        else:
            return ""

    @staticmethod
    def to_data(obj):
        count = obj.split('.')
        if count == 0:
            return int(obj)
        elif count == 1:
            return float(obj)
        else:
            return obj


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


@map_attr(object=Dictionary, array=List, string=String)
@map_attr(number_int=Integer, number_real=Float)
@map_attr(true=Boolean, false=Boolean)
@store_instances("path/to/{d}/{n}.yml", {'n': 'name', 'd': 'category'})
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


class SampleExtended:

    """Sample class using extended attribute types."""

    def __init__(self):
        self.text = ""


@store_instances("path/to/directory/{UUID}.yml", mapping={'level': Level})
class SampleCustomDecorated:

    """Sample class using custom attribute types."""

    def __init__(self, name):
        self.name = name
        self.level = '1.0'


# tests #######################################################################


def test_imports():
    """Verify the package namespace is mapped correctly."""
    # pylint: disable=W0404,W0612,W0621
    from yorm import UUID, store, store_instances, map_attr
    from yorm import Mappable, Converter
    import yorm

    assert store
    assert Converter
    assert yorm.standard.Boolean
    assert yorm.extended.Markdown


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
        sample.object = {'key': 'value'}
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
          key: value
        string: Hello, world!
        'true': false
        """.strip().replace("        ", "") + '\n' == text

        # change file values
        text = """
        array: [4, 5, 6]
        'false': null
        number_int: 42
        number_real: 4.2
        object: {'status': false}
        string: "abc"
        'true': null
        """.strip().replace("        ", "") + '\n'
        with open(sample.yorm_path, 'w') as stream:
            stream.write(text)

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
        mapping = {'object': Dictionary,
                   'array': List,
                   'string': String,
                   'number_int': Integer,
                   'number_real': Float,
                   'true': Boolean,
                   'false': Boolean}
        sample = store(_sample, "path/to/directory/sample.yml", mapping)
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
        sample.object = {'key': 'value'}
        sample.array = [1, 2, 3]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.true = None
        sample.false = None

        # check file values
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
        array:
        - 1
        - 2
        - 3
        'false': null
        number_int: 42
        number_real: 4.2
        object:
          key: value
        string: Hello, world!
        'true': null
        """.strip().replace("        ", "") + '\n' == text

    def test_with(self, tmpdir):
        """Verify standard attribute types dump/load correctly (with)."""
        tmpdir.chdir()
        _sample = SampleStandard()
        mapping = {'string': String,
                   'number_real': Float}
        sample = store(_sample, "path/to/directory/sample.yml", mapping)

        # change object values
        with sample:
            sample.string = "abc"
            sample.number_real = 4.2

            # check for unchanged file values
            with open(sample.yorm_path, 'r') as stream:
                text = stream.read()
            assert "" == text

        # check for cahnged file values
        with open(sample.yorm_path, 'r') as stream:
            text = stream.read()
        assert """
        number_real: 4.2
        string: abc
        """.strip().replace("        ", "") + '\n' == text


@integration
class TestExtended:

    """Integration tests for extended attribute types."""

    def test_function(self, tmpdir):
        """Verify extended attribute types dump/load correctly."""
        tmpdir.chdir()
        _sample = SampleExtended()
        mapping = {'text': Markdown}
        sample = store(_sample, "path/to/directory/sample.yml", mapping)

        # check defaults
        assert "" == sample.text

        # change object values
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
        text = """
        level: 1
        """.strip().replace("        ", "") + '\n'
        with open(sample.yorm_path, 'w') as stream:
            stream.write(text)

        # check object values
        assert '1' == sample.level


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
