# pylint: disable=missing-docstring,unused-variable,expression-not-assigned

import pytest
from expecter import expect

from yorm.types import Object, String, Integer, Float, Boolean


def describe_object():

    obj = None
    pairs = [
        (obj, obj),
        (None, None),
        (1, 1),
        (4.2, 4.2),
        (['a', 'b', 'c'], ['a', 'b', 'c']),
    ]

    def describe_to_value():

        @pytest.mark.parametrize("first,second", pairs)
        def it_converts_correctly(first, second):
            expect(Object.to_value(first)) == second

    def describe_to_data():

        @pytest.mark.parametrize("first,second", pairs)
        def it_converts_correctly(first, second):
            expect(Object.to_data(first)) == second


def describe_string():

    obj = "Hello, world!"
    pairs = [
        (obj, obj),
        (None, ""),
        ("1.2.3", "1.2.3"),
        (['a', 'b', 'c'], "a, b, c"),
    ]
    pairs_to_value = pairs + [
        (1, "1"),
        (4.2, "4.2"),
        (False, "false"),
        (True, "true"),
    ]
    pairs_to_data = pairs + [
        (42, 42),
        (4.2, 4.2),
        ("true", True),
        ("false", False),
    ]

    def describe_to_value():

        @pytest.mark.parametrize("first,second", pairs_to_value)
        def it_converts_correctly(first, second):
            expect(String.to_value(first)) == second

    def describe_to_data():

        @pytest.mark.parametrize("first,second", pairs_to_data)
        def it_converts_correctly(first, second):
            expect(String.to_data(first)) == second


def describe_integer():

    obj = 42
    pairs = [
        (obj, obj),
        (None, 0),
        ("1", 1),
        ("1.1", 1),
        (True, 1),
        (False, 0),
    ]

    def describe_to_value():

        @pytest.mark.parametrize("first,second", pairs)
        def it_converts_correctly(first, second):
            expect(Integer.to_value(first)) == second

        def it_raises_an_exception_when_unable_to_convert():
            with expect.raises(ValueError):
                Integer.to_value("abc")

    def describe_to_data():

        @pytest.mark.parametrize("first,second", pairs)
        def it_converts_correctly(first, second):
            expect(Integer.to_data(first)) == second


def describe_float():

    obj = 4.2
    pairs = [
        (obj, obj),
        (None, 0.0),
        ("1.0", 1.0),
        ("1.1", 1.1),
    ]

    def describe_to_value():

        @pytest.mark.parametrize("first,second", pairs)
        def it_converts_correctly(first, second):
            expect(Float.to_value(first)) == second

        def it_raises_an_exception_when_unable_to_convert():
            with expect.raises(ValueError):
                Float.to_value("abc")

    def describe_to_data():

        @pytest.mark.parametrize("first,second", pairs)
        def it_converts_correctly(first, second):
            expect(Float.to_data(first)) == second


def describe_boolean():

    obj = True
    pairs = [
        (obj, obj),
        (None, False),
        (0, False),
        (1, True),
        ("", False),
        ("True", True),
        ("False", False),
        ("true", True),
        ("false", False),
        ("T", True),
        ("F", False),
        ("yes", True),
        ("no", False),
        ("Y", True),
        ("N", False),
        ("enabled", True),
        ("disabled", False),
        ("on", True),
        ("off", False),
        ("Hello, world!", True)
    ]

    def describe_to_value():

        @pytest.mark.parametrize("first,second", pairs)
        def it_converts_correctly(first, second):
            expect(Boolean.to_value(first)) == second

    def describe_to_data():

        @pytest.mark.parametrize("first,second", pairs)
        def it_converts_correctly(first, second):
            expect(Boolean.to_data(first)) == second
