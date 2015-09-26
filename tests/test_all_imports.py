# pylint:disable=W0404,W0612,C

"""Integration tests the package namespace."""

import pytest


def test_top():

    import yorm

    assert yorm.bases
    assert yorm.converters.Integer
    assert yorm.converters.extended.Markdown


def test_from_top():

    # Constants
    from yorm import UUID  # filename placeholder

    # Classes
    from yorm import Mappable  # base class for mapped objects
    from yorm import Converter, Convertible  # base class for converters

    # Decorators
    from yorm import sync  # enables mapping on a class's instance objects
    from yorm import sync_instances  # alias for the class decorator
    from yorm import attr  # alternate API to identify mapped attributes

    # Functions
    from yorm import sync  # enables mapping on an instance object
    from yorm import sync_object  # alias for the mapping function
    from yorm import update  # fetch (if necessary) and store a mapped object
    from yorm import update_object  # fetch (optional force) a mapped object
    from yorm import update_file  # store a mapped object


def test_from_nested():

    # Classes
    from yorm.converters import Integer
    from yorm.converters.standard import String
    from yorm.converters.extended import Markdown
    from yorm.converters.containers import List
