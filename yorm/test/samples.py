"""Sample classes for unit tests."""

from yorm import attr
from yorm.converters import Integer, Float, String
from yorm.converters import Dictionary, List
from yorm.converters import AttributeDictionary, SortedList


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


@attr(all=Float)
class SampleSortedList(SortedList):

    """Sample sorted list container."""


class UnknownSortedList(SortedList):

    """Sample list container."""


@attr(var1=Integer, var2=String)
class SampleAttributeDictionary(AttributeDictionary):

    """Sample dictionary container with initialization."""

    def __init__(self, var1, var2, var3):
        super().__init__()
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3
