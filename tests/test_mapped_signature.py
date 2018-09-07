"""Integration tests to ensure a mapped object's signature is unchanged."""

# pylint: disable=redefined-outer-name,unused-variable,expression-not-assigned

import pytest
from expecter import expect

from yorm import decorators


class SampleWithMagicMethods:

    def __init__(self):
        self.values = []

    def __setattr__(self, name, value):
        if name == 'foobar':
            self.values.append(('__setattr__', name, value))
        super().__setattr__(name, value)


@pytest.yield_fixture
def mapped():
    import yorm
    yorm.settings.fake = True
    yield decorators.sync(SampleWithMagicMethods(), "sample.yml")
    yorm.settings.fake = False


@pytest.fixture
def unmapped():
    return SampleWithMagicMethods()


def fuzzy_repr(obj):
    return repr(obj).split(" object at ")[0] + ">"


def describe_mapped_object():

    def it_retains_representation(mapped, unmapped):
        expect(fuzzy_repr(mapped)) == fuzzy_repr(unmapped)

    def it_retains_docstring(mapped, unmapped):
        expect(mapped.__doc__) == unmapped.__doc__

    def it_retains_class(mapped, unmapped):
        expect(mapped.__class__) == unmapped.__class__

    def it_retains_magic_methods(mapped):
        setattr(mapped, 'foobar', 42)
        expect(mapped.values) == [('__setattr__', 'foobar', 42)]

    def it_does_not_affect_unmapped_objects(mapped, unmapped):
        expect(hasattr(mapped, '__mapper__')) is True
        expect(hasattr(unmapped, '__mapper__')) is False
        expect(hasattr(mapped.__setattr__, '_modified_by_yorm')) is True
        expect(hasattr(unmapped.__setattr__, '_modified_by_yorm')) is False
