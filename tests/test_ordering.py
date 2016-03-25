# pylint: disable=redefined-outer-name

import pytest

import yorm

from . import strip


@yorm.attr(string=yorm.types.String)
@yorm.attr(number_int=yorm.types.Integer)
@yorm.attr(number_real=yorm.types.Float)
@yorm.attr(truthy=yorm.types.Boolean)
@yorm.attr(falsey=yorm.types.Boolean)
@yorm.sync("sample.yml")
class Sample:
    """Sample class with ordered attributes."""


@pytest.fixture
def sample(tmpdir):
    tmpdir.chdir()
    return Sample()


def test_attribute_order_is_maintained(sample):
    sample.string = "Hello, world!"
    sample.number_int = 42
    sample.number_real = 4.2
    sample.truthy = False
    sample.falsey = True

    assert strip("""
    string: Hello, world!
    number_int: 42
    number_real: 4.2
    truthy: false
    falsey: true
    """) == sample.__mapper__.text
