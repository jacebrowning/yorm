"""Integration tests."""

import pytest
import yaml

from yorm import yormalize, yattr, Yattribute
from yorm.basic import Dictionary, List, String, Integer, Float, Boolean

integration = pytest.mark.integration


# custom types ################################################################


class Level(Yattribute):

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


class SampleBasic:

    """Sample class using basic types."""

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


@yattr(object=Dictionary, array=List, string=String)
@yattr(number_int=Integer, number_real=Float)
@yattr(true=Boolean, false=Boolean)
@yormalize("path/to/{directory}", "name", directory="category")
class SampleBasicDecorated:

    """Sample class using basic types."""

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


@yormalize("path/to/directory", "name", attrs={'level': Level})
class SampleCustomDecorated:

    """Sample class using custom types."""

    def __init__(self, name):
        self.name = name
        self.level = '1.0'


# tests #######################################################################


@integration
class TestBasic:

    """Integration tests for basic attribute types."""

    def test_decorator(self):
        sample = SampleBasicDecorated('sample')

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
        _sample = SampleBasic()
        sample = yormalize(_sample, attrs={'object': Dictionary,
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
