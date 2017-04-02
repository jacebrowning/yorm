# pylint: disable=missing-docstring,unused-variable,expression-not-assigned,singleton-comparison

import pytest
from expecter import expect

from yorm.decorators import attr
from yorm.types.standard import Integer, String, Float
from yorm.types.extended import (NullableString, Markdown,
                                 AttributeDictionary, SortedList)


def describe_nullable_string():

    def describe_to_value():

        def it_allows_none():
            expect(NullableString.to_value(None)).is_none()

    def describe_to_data():

        def it_allows_none():
            expect(NullableString.to_data(None)).is_none()


def describe_markdown():

    obj = "This is **the** sentence."
    data_value = [
        (obj, obj),
        (None, ""),
        (['a', 'b', 'c'], "a, b, c"),
        ("This is\na sentence.", "This is a sentence."),
        ("Sentence one.\nSentence two.", "Sentence one. Sentence two."),
    ]
    value_data = [
        (obj, obj + '\n'),
        ("Sentence one. Sentence two.", "Sentence one.\nSentence two.\n"),
        ("", ""),
        (" \t ", ""),
    ]

    def describe_to_value():

        @pytest.mark.parametrize("data,value", data_value)
        def it_converts_correctly(data, value):
            expect(Markdown.to_value(data)) == value

    def describe_to_data():

        @pytest.mark.parametrize("value,data", value_data)
        def it_converts_correctly(value, data):
            expect(Markdown.to_data(value)) == data


def describe_attribute_dictionary():

    @pytest.fixture
    def cls():
        @attr(var1=Integer)
        @attr(var2=String)
        class MyAttributeDictionary(AttributeDictionary): pass
        return MyAttributeDictionary

    @pytest.fixture
    def cls_with_init():
        @attr(var1=Integer)
        class MyAttributeDictionary(AttributeDictionary):
            def __init__(self, *args, var2="42", **kwargs):
                super().__init__(*args, **kwargs)
                self.var2 = var2
        return MyAttributeDictionary

    @pytest.fixture
    def cls_with_args():
        @attr(var1=Integer)
        class MyAttributeDictionary(AttributeDictionary):
            def __init__(self, var1, var2="42"):
                super().__init__()
                self.var1 = var1
                self.var2 = var2
        return MyAttributeDictionary

    def it_cannot_be_used_directly():
        with expect.raises(NotImplementedError):
            AttributeDictionary.to_value(None)
        with expect.raises(NotImplementedError):
            AttributeDictionary.to_data(None)

    def it_has_keys_available_as_attributes(cls):
        converter = cls()

        value = converter.to_value({'var1': 1, 'var2': "2"})

        expect(value.var1) == 1
        expect(value.var2) == "2"

    def it_adds_extra_attributes_from_init(cls_with_init):
        converter = cls_with_init()

        value = converter.to_value({'var1': 1})
        print(value.__dict__)

        expect(value.var1) == 1
        expect(value.var2) == "42"

    def it_allows_positional_arguments(cls_with_args):
        converter = cls_with_args(99)

        value = converter.to_value({'var1': 1})
        print(value.__dict__)

        expect(value.var1) == 1
        expect(hasattr(value, 'var2')) == False


def describe_sorted_list():

    @attr(all=Float)
    class SampleSortedList(SortedList):
        """Sample sorted list."""

    class UnknownSortedList(SortedList):
        """Sample list without a type."""

    @pytest.fixture
    def converter():
        return SampleSortedList()

    def it_cannot_be_used_directly():
        with expect.raises(NotImplementedError):
            SortedList.to_value(None)
        with expect.raises(NotImplementedError):
            SortedList.to_data(None)

    def it_cannot_be_subclassed_without_a_type():
        with expect.raises(NotImplementedError):
            UnknownSortedList.to_value(None)
        with expect.raises(NotImplementedError):
            UnknownSortedList.to_data(None)

    def describe_to_data():

        def it_sorts(converter):
            data = converter.to_data([4, 2, 0, 1, 3])
            expect(data) == [0.0, 1.0, 2.0, 3.0, 4.0]
