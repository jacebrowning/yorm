"""Sample converters and mapped classes for tests."""

from unittest.mock import Mock

from yorm.bases import Converter, Mappable
from yorm.utilities import sync, attr
from yorm.converters import Dictionary, List
from yorm.converters import String, Integer, Float, Boolean
from yorm.converters import AttributeDictionary, SortedList


# sample converters ###########################################################


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


# mock containers #############################################################


class MockConverter(Converter):

    """Sample converter class."""

    @classmethod
    def create_default(cls):
        return None

    @classmethod
    def to_value(cls, _):
        return None

    @classmethod
    def to_data(cls, _):
        return None


class MockConverter0(MockConverter):

    """Sample converter class."""


class MockConverter1(MockConverter):

    """Sample converter class."""


class MockConverter2(MockConverter):

    """Sample converter class."""


class MockConverter3(MockConverter):

    """Sample converter class."""


class MockConverter4(MockConverter):

    """Sample converter class."""

    pass


# sample containers ###########################################################


class EmptyDictionary(Dictionary):

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


@attr(abc=Integer)
class SampleDictionary(Dictionary):

    """Sample dictionary container."""


@attr(var1=Integer, var2=String)
class SampleDictionaryWithInitialization(Dictionary):

    """Sample dictionary container with initialization."""

    def __init__(self, var1, var2, var3):
        super().__init__()
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3


@attr(all=String)
class StringList(List):

    """Sample list container."""


class UnknownList(List):

    """Sample list container."""

    pass


# sample extended containers ##################################################


@attr(var1=Integer, var2=String)
class SampleAttributeDictionary(AttributeDictionary):

    """Sample dictionary container with initialization."""

    def __init__(self, var1, var2, var3):
        super().__init__()
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3


@attr(all=Float)
class SampleSortedList(SortedList):

    """Sample sorted list container."""


class UnknownSortedList(SortedList):

    """Sample list container."""

    pass


# mock mapped classes #########################################################


class MockMappable(Mappable):

    """Sample mappable class."""

    yorm_mapper = Mock()
    yorm_mapper.attrs = {}


# sample mapped classes #######################################################


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


@attr(string=String)
@sync("sample.yml", auto=False)
class SampleDecoratedAutoOff:

    """Sample class with automatic storage turned off."""

    def __init__(self):
        self.string = ""

    def __repr__(self):
        return "<auto off {}>".format(id(self))


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
