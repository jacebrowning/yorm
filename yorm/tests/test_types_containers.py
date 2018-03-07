# pylint: disable=missing-docstring,no-self-use,no-member,misplaced-comparison-constant,expression-not-assigned

import logging
from unittest.mock import patch, Mock

import pytest
from expecter import expect

import yorm
from yorm import common
from yorm.decorators import attr
from yorm.types import Dictionary, List
from yorm.types import String, Integer

from . import strip

log = logging.getLogger(__name__)


# CLASSES ######################################################################


@attr(abc=Integer)
class SampleDictionary(Dictionary):
    """Sample dictionary container."""


@attr(var1=Integer)
@attr(var2=String)
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


# TESTS ########################################################################


class TestDictionary:
    """Unit tests for the `Dictionary` container."""

    obj = {'abc': 123}

    class SampleClass:

        def __init__(self):
            self.abc = 42

    class SampleClass2:

        def __init__(self):
            self.unmapped = Mock()

    data_value = [
        (obj, obj),
        (None, {'abc': 0}),
        ("key=value", {'key': "value", 'abc': 0}),
        ("key=", {'key': "", 'abc': 0}),
        ("key", {'key': None, 'abc': 0}),
    ]

    value_data = [
        (obj, obj),
        (SampleClass(), {'abc': 42}),
        (SampleClass2(), {'abc': 0}),
        ([], {'abc': 0}),
    ]

    def setup_method(self, _):
        """Reset the class' mapped attributes before each test."""
        common.attrs[SampleDictionary] = {'abc': Integer}

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert value == SampleDictionary.to_value(data)

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == SampleDictionary.to_data(value)

    def test_not_implemented(self):
        """Verify `Dictionary` cannot be used directly."""
        with pytest.raises(NotImplementedError):
            Dictionary()

    def test_dict_as_object(self):
        """Verify a `Dictionary` can be used as an attribute."""
        dictionary = SampleDictionaryWithInitialization(1, 2, 3.0)
        value = {'var1': 1, 'var2': '2'}
        value2 = dictionary.to_value(dictionary)
        assert value == value2
        # keys are not accessible as attributes
        assert not hasattr(value2, 'var1')
        assert not hasattr(value2, 'var2')
        assert not hasattr(value2, 'var3')

    def test_unknown_attrributes_are_ignored(self):
        obj = SampleDictionary.create_default()
        obj.update_value({'key': "value", 'abc': 7}, auto_track=False)
        assert {'abc': 7} == obj


class TestList:
    """Unit tests for the `List` container."""

    obj = ["a", "b", "c"]

    data_value = [
        (obj, obj),
        (None, []),
        ([None], []),
        ("a b c", ["a", "b", "c"]),
        ("a,b,c", ["a", "b", "c"]),
        ("abc", ["abc"]),
        ("a\nb\nc", ["a", "b", "c"]),
        (4.2, ['4.2']),
        (("a", "b"), ["a", "b"]),
    ]

    value_data = [
        (obj, obj),
        ([], [None]),
    ]

    @pytest.mark.parametrize("data,value", data_value)
    def test_to_value(self, data, value):
        """Verify input data is converted to values."""
        assert value == StringList.to_value(data)

    @pytest.mark.parametrize("value,data", value_data)
    def test_to_data(self, value, data):
        """Verify values are converted to output data."""
        assert data == StringList.to_data(value)

    def test_item_type(self):
        """Verify list item type can be determined."""
        assert String == StringList.item_type

    def test_item_type_none(self):
        """Verify list item type defaults to None."""
        assert None is UnknownList.item_type

    def test_not_implemented(self):
        """Verify `List` cannot be used directly."""
        with pytest.raises(NotImplementedError):
            List()
        with pytest.raises(NotImplementedError):
            UnknownList()

    def test_shortened_syntax(self):
        cls = List.of_type(Integer)
        expect(cls.__name__) == "IntegerList"
        expect(common.attrs[cls]) == {'all': Integer}


class TestExtensions:
    """Unit tests for extensions to the container classes."""

    class FindMixin:

        def find(self, value):
            for value2 in self:
                if value.lower() == value2.lower():
                    return value2
            return None

    @yorm.attr(a=yorm.types.String)
    class MyDictionary(Dictionary, FindMixin):
        pass

    @yorm.attr(all=yorm.types.String)
    class MyList(List, FindMixin):
        pass

    def test_converted_dict_keeps_type(self):
        my_dict = self.MyDictionary()
        my_dict['a'] = 1
        my_dict2 = self.MyDictionary.to_value(my_dict)
        assert 'a' == my_dict2.find('A')
        assert None is my_dict2.find('B')

    def test_converted_list_keeps_type(self):
        my_list = self.MyList()
        my_list.append('a')
        my_list2 = self.MyList.to_value(my_list)
        assert 'a' == my_list2.find('A')
        assert None is my_list2.find('B')


@patch('yorm.settings.fake', True)
class TestReservedNames:

    class MyObject:

        def __init__(self, items=None):
            self.items = items or []

        def __repr__(self):
            return "<my_object>"

    def test_list_named_items(self):
        my_object = self.MyObject()
        yorm.sync_object(my_object, "fake/path", {'items': StringList})

        log.info("Appending value to list of items...")
        my_object.items.append('foo')

        log.info("Checking object contents...")
        assert strip("""
        items:
        - foo
        """) == my_object.__mapper__.text

        log.info("Writing new file contents...")
        my_object.__mapper__.text = strip("""
        items:
        - bar
        """)

        log.info("Checking file contents...")
        assert ['bar'] == my_object.items
