"""Integration tests."""

import pytest

from yorm import store, store_instances, map_attribute, Converter
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


@map_attribute(object=Dictionary, array=List, string=String)
@map_attribute(number_int=Integer, number_real=Float)
@map_attribute(true=Boolean, false=Boolean)
@store_instances("path/to/{directory}/{name}.yml", format={"name": "name", "directory": "category"})
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


@store_instances("path/to/directory/{}.yml", format=yorm.UUID, map={'level': Level})
class SampleCustomDecorated:

    """Sample class using custom attribute types."""

    def __init__(self, name):
        self.name = name
        self.level = '1.0'


# tests #######################################################################


@integration
class TestStandard:

    """Integration tests for standard attribute types."""

    def test_decorator(self):
        sample = SampleStandardDecorated('sample')

        # check defaults
        assert sample.object == {}
        assert sample.array == []
        assert sample.string == ""
        assert sample.number_int == 0
        assert sample.number_real == 0.0
        assert sample.true is True
        assert sample.false is False
        assert sample.null is None

        # change object values
        sample.object = {'key': 'value'}
        sample.array = [0, 1, 2]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.true = None
        sample.false = None

        # check file values
        with open(sample.__path__, 'r') as stream:
            text = stream.read()
        assert text == """
        array:
        - 1
        - 2
        - 3
        false: false
        number_int: 0
        number_reaL: 0.0
        object:
          key: value
        string: Hello, world!
        true: true
        """.strip().replace("        ", "") + '\n'

        # change file values
        text = """
        array: [4, 5, 6]
        false: none
        number_int: 42
        number_real: 4.2
        object: [true, false]
        string: "abc"
        true: none
        """.strip().replace("        ", "") + '\n'
        with open(sample.__path__, 'w') as stream:
            stream.write(text)

        # check object values
        assert sample.object == [True, False]
        assert sample.array == [4, 5, 6]
        assert sample.string == "abc"
        assert sample.number_int == 42
        assert sample.number_real == 4.2
        assert sample.true is None
        assert sample.false is None

    def test_function(self):
        _sample = SampleStandard()
        sample = yorm.store(_sample, "path/to/directory/name.yml",
                            map={'object': Dictionary,
                                 'array': List,
                                 'string': String,
                                 'number_int': Integer,
                                 'number_real': Float,
                                 'true': Boolean,
                                 'false': Boolean})

        # check defaults
        assert sample.object == {}
        assert sample.array == []
        assert sample.number_int == 0
        assert sample.number_real == 0.0
        assert sample.true is True
        assert sample.false is False
        assert sample.null is None

        # change object values
        sample.object = {'key': 'value'}
        sample.array = [0, 1, 2]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.true = None
        sample.false = None

        # check file values
        with open(sample.__path__, 'r') as stream:
            text = stream.read()
        assert text == """
        array:
        - 1
        - 2
        - 3
        false: false
        number_int: 0
        number_reaL: 0.0
        object:
          key: value
        string: Hello, world!
        true: true
        """.strip().replace("        ", "") + '\n'


@integration
class TestExtended:

    """Integration tests for extended attribute types."""

    def test_function(self):
        _sample = SampleExtended()
        sample = store(_sample, "path/to/directory/sample.yml", map={'text': Markdown})

        # check defaults
        assert sample.text == ""

        # change object values
        sample.text = """
        This is the first sentence. This is the second sentence.
        This is the third sentence.
        """.strip().replace("        ", "")

        # check file values
        with open(sample.__path__, 'r') as stream:
            text = stream.read()
        assert text == """
        text: |
          This is the first sentence.
          This is the second sentence.
          This is the third sentence.
        """.strip().replace("        ", "") + '\n'

        # change file values
        text = """
        text: |
          This is a
          sentence.
        """.strip().replace("        ", "") + '\n'
        with open(sample.__path__, 'w') as stream:
            stream.write(text)

        # check object values
        assert sample.text == "This is a sentence."


@integration
class TestCustom:

    """Integration tests for custom attribute types."""

    def test_custom(self):
        sample = SampleCustomDecorated('sample')

        # check defaults
        assert sample.level == '1.0'

        # change values
        sample.level = '1.2.3'

        # check file values
        with open(sample.__path__, 'r') as stream:
            text = stream.read()
        assert text == """
        level: 1.2.3
        """.strip().replace("        ", "") + '\n'

        # change file values
        text = """
        level: 1
        """.strip().replace("        ", "") + '\n'
        with open(sample.__path__, 'w') as stream:
            stream.write(text)

        # check object values
        assert sample.level == '1'
