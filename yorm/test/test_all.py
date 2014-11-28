#!/usr/bin/env python
# pylint:disable=R0201

"""Integration tests for the `yorm` package."""

import pytest

from yorm import store, store_instances, map_attr, Converter
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


@map_attr(key=String)
class SingleKeyDictionary(Dictionary):

    """Sample dictionary container."""


@map_attr(all=Integer)
class IntegerList(List):

    """Sample list container."""


@map_attr(status=Boolean, label=String)
class StatusDictionary(Dictionary):

    """Sample dictionary container."""


@map_attr(all=StatusDictionary)
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


@map_attr(object=EmptyDictionary, array=IntegerList, string=String)
@map_attr(number_int=Integer, number_real=Float)
@map_attr(true=Boolean, false=Boolean)
@store_instances("path/to/{self.category}/{self.name}.yml")
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


@map_attr(string=String, number_real=Float)
@store_instances("sample.yml", auto=False)
class SampleDecoratedNoAuto:

    """Sample class with automatic storate turned off."""

    def __init__(self):
        self.string = ""
        self.number_real = 0.0

    def __repr__(self):
        return "<no auto {}>".format(id(self))


@map_attr(string=String, number_real=Float)
class SampleDecoratedNoPath:

    """Sample class with a manually mapped path."""

    def __init__(self):
        self.string = ""
        self.number_real = 0.0

    def __repr__(self):
        return "<no path {}>".format(id(self))


@store_instances("sample.yml")
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


@store_instances("path/to/directory/{UUID}.yml", mapping={'level': Level})
class SampleCustomDecorated:

    """Sample class using custom attribute types."""

    def __init__(self, name):
        self.name = name
        self.level = '1.0'

    def __repr__(self):
        return "<custom {}>".format(id(self))


# tests #######################################################################


def test_imports():
    """Verify the package namespace is mapped correctly."""
    # pylint: disable=W0404,W0612,W0621
    import yorm

    from yorm import UUID, store, store_instances, map_attr
    from yorm import Mappable, Converter

    from yorm.standard import String
    from yorm.extended import Markdown
    from yorm.container import List

    assert store
    assert Converter
    assert yorm.standard.Boolean
    assert yorm.extended.Markdown
    assert yorm.container.Dictionary


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
        mapping = {'object': SingleKeyDictionary,
                   'array': IntegerList,
                   'string': String,
                   'number_int': Integer,
                   'number_real': Float,
                   'true': Boolean,
                   'false': Boolean}
        sample = store(_sample, "path/to/directory/sample.yml", mapping)
        assert "path/to/directory/sample.yml" == sample.yorm_path

        # check defaults
        assert {'key': ''} == sample.object
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
        mapping = {'string': String,
                   'number_real': Float}
        sample = store(_sample, "sample.yml", mapping, auto=False)

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
        sample.yorm_mapper.store(sample)
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
        sample = store(SampleDecoratedNoPath(), "sample.yml")

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
        mapping = {'count': Integer,
                   'results': StatusDictionaryList}
        sample = store(_sample, "sample.yml", mapping)

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
        text = """
        object: {'key': 'value'}
        array: [1, '2', '3.0']
        """.strip().replace("        ", "") + '\n'
        with open(sample.yorm_path, 'w') as stream:
            stream.write(text)

            # (a mapped attribute must be read first to trigger retrieving)
        sample.yorm_mapper.retrieve(sample)

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
class TestInit:

    """Integration tests for initializing mapped classes."""

    def test_retrieve_from_existing(self, tmpdir):
        """Verify attributes are loaded from an existing file."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        sample2 = SampleStandardDecorated('sample')
        assert sample2.yorm_path == sample.yorm_path

        # change object values
        sample.object = {'key2': 'value'}
        sample.array = [0, 1, 2]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.true = True
        sample.false = False

        # check object values
        assert {'key2': 'value', 'status': False} == sample2.object
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
