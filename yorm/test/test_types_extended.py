# pylint: disable=missing-docstring,unused-variable,expression-not-assigned

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

    @attr(var1=Integer)
    @attr(var2=String)
    class SampleAttributeDictionary(AttributeDictionary):
        """Sample attribute dictionary."""

    @pytest.fixture
    def converter():
        return SampleAttributeDictionary()

    def it_cannot_be_used_directly():
        with expect.raises(NotImplementedError):
            AttributeDictionary.to_value(None)
        with expect.raises(NotImplementedError):
            AttributeDictionary.to_data(None)

    def it_has_keys_available_as_attributes(converter):
        value = converter.to_value({'var1': 1, 'var2': "2"})
        expect(value.var1) == 1
        expect(value.var2) == "2"


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
