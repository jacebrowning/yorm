"""Integration tests."""

import pytest

from yorm import yormalize, yattr, Yattribute
from yorm.basic import Dictionary, List, String, Integer, Float, Boolean

integration = pytest.mark.integration


# basic types ################################################################


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


@integration
class TestBasic:

    """Integration tests for basic attribute types."""

    def test_decorator(self):

        sample = SampleBasicDecorated('sample')

        assert sample.object == {}
        assert sample.array == []
        assert sample.string == ""
        assert sample.number_int == 0
        assert sample.number_real == 0.0
        assert sample.true is True
        assert sample.false is False
        assert sample.null is None

        # TODO: change values

    def test_function(self):

        _sample = SampleBasic()
        sample = yormalize(_sample, attrs={'object': Dictionary,
                                           'array': List,
                                           'string': String,
                                           'number_int': Integer,
                                           'number_real':Float,
                                           'true': Boolean,
                                           'false': Boolean})

        assert sample.object == {}
        assert sample.array == []
        assert sample.number_int == 0
        assert sample.number_real == 0.0
        assert sample.true is True
        assert sample.false is False
        assert sample.null is None

        # TODO: change values


# complex types ##############################################################

# TODO: add tests for complex types

# custom types ###############################################################


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


@yormalize("path/to/directory", "name", attrs={'level': Level})
class SampleCustomDecorated:

    """Sample class using custom types."""

    def __init__(self, name):
        self.name = name
        self.level = '1.0'


@integration
class TestCustom:

    """Integration tests for custom attribute types."""

    def test_custom(self):

        sample = SampleCustomDecorated('sample')

        assert sample.level == '1.0'

        # TODO: change values
