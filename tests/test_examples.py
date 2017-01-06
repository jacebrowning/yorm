"""Integration tests for the package."""
# pylint: disable=missing-docstring,no-self-use,no-member,misplaced-comparison-constant,attribute-defined-outside-init

import yorm
from yorm.types import Object, String, Integer, Float, Boolean
from yorm.types import Markdown, Dictionary, List

from . import strip, refresh_file_modification_times, log


# CLASSES ######################################################################


class EmptyDictionary(Dictionary):
    """Sample dictionary container."""


@yorm.attr(all=Integer)
class IntegerList(List):
    """Sample list container."""


class SampleStandard:
    """Sample class using standard attribute types."""

    def __init__(self):
        # https://docs.python.org/3.4/library/json.html#json.JSONDecoder
        self.object = {}
        self.array = []
        self.string = ""
        self.number_int = 0
        self.number_real = 0.0
        self.truthy = True
        self.falsey = False
        self.null = None

    def __repr__(self):
        return "<standard {}>".format(id(self))


@yorm.attr(array=IntegerList)
@yorm.attr(falsey=Boolean)
@yorm.attr(number_int=Integer)
@yorm.attr(number_real=Float)
@yorm.attr(object=EmptyDictionary)
@yorm.attr(string=String)
@yorm.attr(truthy=Boolean)
@yorm.sync("tmp/{self.category}/{self.name}.yml")
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
        self.truthy = True
        self.falsey = False
        self.null = None

    def __repr__(self):
        return "<decorated {}>".format(id(self))


@yorm.attr(label=String)
@yorm.attr(status=Boolean)
class StatusDictionary(Dictionary):
    """Sample dictionary container."""


@yorm.attr(all=StatusDictionary)
class StatusDictionaryList(List):
    """Sample list container."""


class Level(String):
    """Sample custom attribute."""

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


@yorm.sync("tmp/directory/{UUID}.yml", attrs={'level': Level})
class SampleCustomDecorated:
    """Sample class using custom attribute types."""

    def __init__(self, name):
        self.name = name
        self.level = '1.0'

    def __repr__(self):
        return "<custom {}>".format(id(self))


@yorm.attr(string=String)
@yorm.sync("tmp/sample.yml", auto_save=False)
class SampleDecoratedAutoOff:
    """Sample class with automatic storage turned off."""

    def __init__(self):
        self.string = ""

    def __repr__(self):
        return "<auto save off {}>".format(id(self))


@yorm.sync("tmp/sample.yml", auto_track=True)
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


class SampleNested:
    """Sample class using nested attribute types."""

    def __init__(self):
        self.count = 0
        self.results = []

    def __repr__(self):
        return "<nested {}>".format(id(self))

# TESTS ########################################################################


class TestStandard:
    """Integration tests for standard attribute types."""

    @yorm.attr(status=yorm.types.Boolean)
    class StatusDictionary(Dictionary):
        pass

    def test_decorator(self, tmpdir):
        """Verify standard attribute types dump/parse correctly (decorator)."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        assert "tmp/default/sample.yml" == sample.__mapper__.path

        log("Checking object default values...")
        assert {} == sample.object
        assert [] == sample.array
        assert "" == sample.string
        assert 0 == sample.number_int
        assert 0.0 == sample.number_real
        assert True is sample.truthy
        assert False is sample.falsey
        assert None is sample.null

        log("Changing object values...")
        sample.object = {'key2': 'value'}
        sample.array = [0, 1, 2]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.truthy = False
        sample.falsey = True

        log("Checking file contents...")
        assert strip("""
        array:
        - 0
        - 1
        - 2
        falsey: true
        number_int: 42
        number_real: 4.2
        object: {}
        string: Hello, world!
        truthy: false
        """) == sample.__mapper__.text

        log("Changing file contents...")
        refresh_file_modification_times()
        sample.__mapper__.text = strip("""
        array: [4, 5, 6]
        falsey: null
        number_int: 42
        number_real: '4.2'
        object: {'status': false}
        string: "abc"
        truthy: null
        """)

        log("Checking object values...")
        assert {'status': False} == sample.object
        assert [4, 5, 6] == sample.array
        assert "abc" == sample.string
        assert 42 == sample.number_int
        assert 4.2 == sample.number_real
        assert False is sample.truthy
        assert False is sample.falsey

    def test_function(self, tmpdir):
        """Verify standard attribute types dump/parse correctly (function)."""
        tmpdir.chdir()
        _sample = SampleStandard()
        attrs = {'object': self.StatusDictionary,
                 'array': IntegerList,
                 'string': String,
                 'number_int': Integer,
                 'number_real': Float,
                 'truthy': Boolean,
                 'falsey': Boolean}
        sample = yorm.sync(_sample, "tmp/directory/sample.yml", attrs)
        assert "tmp/directory/sample.yml" == sample.__mapper__.path

        # check defaults
        assert {'status': False} == sample.object
        assert [] == sample.array
        assert "" == sample.string
        assert 0 == sample.number_int
        assert 0.0 == sample.number_real
        assert True is sample.truthy
        assert False is sample.falsey
        assert None is sample.null

        # change object values
        sample.object = {'key': 'value'}
        sample.array = [1, 2, 3]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.truthy = None
        sample.falsey = 1

        # check file values
        assert strip("""
        array:
        - 1
        - 2
        - 3
        falsey: true
        number_int: 42
        number_real: 4.2
        object:
          status: false
        string: Hello, world!
        truthy: false
        """) == sample.__mapper__.text

    def test_function_to_json(self, tmpdir):
        """Verify standard attribute types dump/parse correctly (function)."""
        tmpdir.chdir()
        _sample = SampleStandard()
        attrs = {'object': self.StatusDictionary,
                 'array': IntegerList,
                 'string': String,
                 'number_int': Integer,
                 'number_real': Float,
                 'truthy': Boolean,
                 'falsey': Boolean}
        sample = yorm.sync(_sample, "tmp/directory/sample.json", attrs)
        assert "tmp/directory/sample.json" == sample.__mapper__.path

        # check defaults
        assert {'status': False} == sample.object
        assert [] == sample.array
        assert "" == sample.string
        assert 0 == sample.number_int
        assert 0.0 == sample.number_real
        assert True is sample.truthy
        assert False is sample.falsey
        assert None is sample.null

        # change object values
        sample.object = {'key': 'value'}
        sample.array = [1, 2, 3]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.truthy = None
        sample.falsey = 1

        # check file values
        assert strip("""
        {
            "array": [
                1,
                2,
                3
            ],
            "falsey": true,
            "number_int": 42,
            "number_real": 4.2,
            "object": {
                "status": false
            },
            "string": "Hello, world!",
            "truthy": false
        }
        """, tabs=2, end='') == sample.__mapper__.text

    def test_auto_off(self, tmpdir):
        """Verify file updates are disabled with auto save off."""
        tmpdir.chdir()
        sample = SampleDecoratedAutoOff()

        sample.string = "hello"
        assert "" == sample.__mapper__.text

        sample.__mapper__.auto_save = True
        sample.string = "world"

        assert strip("""
        string: world
        """) == sample.__mapper__.text


class TestContainers:
    """Integration tests for attribute containers."""

    def test_nesting(self, tmpdir):
        """Verify standard attribute types can be nested."""
        tmpdir.chdir()
        _sample = SampleNested()
        attrs = {'count': Integer,
                 'results': StatusDictionaryList}
        sample = yorm.sync(_sample, "tmp/sample.yml", attrs, auto_track=True)

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
        """) == sample.__mapper__.text

        # change file values
        refresh_file_modification_times()
        sample.__mapper__.text = strip("""
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
        sample.__mapper__.text = strip("""
        object: {'key': 'value'}
        array: [1, '2', '3.0']
        """)

        # (a mapped attribute must be read first to trigger retrieving)
        sample.__mapper__.load()

        # check object values
        assert {'key': 'value'} == sample.object
        assert [1, '2', '3.0'] == sample.array

        # check object types
        assert Object == sample.__mapper__.attrs['object']
        assert Object == sample.__mapper__.attrs['array']


class TestExtended:
    """Integration tests for extended attribute types."""

    def test_function(self, tmpdir):
        """Verify extended attribute types dump/parse correctly."""
        tmpdir.chdir()
        _sample = SampleExtended()
        attrs = {'text': Markdown}
        sample = yorm.sync(_sample, "tmp/directory/sample.yml", attrs)

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
        """) == sample.__mapper__.text

        # change file values
        refresh_file_modification_times()
        sample.__mapper__.text = strip("""
        text: |
          This is a
          sentence.
        """)

        # check object values
        assert "This is a sentence." == sample.text


class TestCustom:
    """Integration tests for custom attribute types."""

    def test_decorator(self, tmpdir):
        """Verify custom attribute types dump/parse correctly."""
        tmpdir.chdir()
        sample = SampleCustomDecorated('sample')

        # check defaults
        assert '1.0' == sample.level

        # change values
        sample.level = '1.2.3'

        # check file values
        assert strip("""
        level: 1.2.3
        """) == sample.__mapper__.text

        # change file values
        refresh_file_modification_times()
        sample.__mapper__.text = strip("""
        level: 1
        """)

        # check object values
        assert '1' == sample.level
