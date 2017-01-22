# pylint: disable=redefined-outer-name,expression-not-assigned,attribute-defined-outside-init,no-member

from expecter import expect

import yorm
from yorm.types import List, Float

from . import strip


@yorm.attr(things=List.of_type(Float))
@yorm.sync("tmp/example.yml")
class Example:
    """An example class mapping a list using the shortened syntax."""


def test_list_mapping_using_shortened_syntax():
    obj = Example()
    obj.things = [1, 2.0, "3"]

    expect(obj.__mapper__.text) == strip("""
    things:
    - 1.0
    - 2.0
    - 3.0
    """)
