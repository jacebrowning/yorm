"""Integration tests for the package namespace."""
# pylint: disable=missing-docstring,no-self-use,unused-variable


def test_top():
    import yorm
    assert yorm.bases
    assert yorm.types.Integer
    assert yorm.types.extended.Markdown


def test_from_top_constants():
    from yorm import UUID  # filename placeholder


def test_from_top_clases():
    from yorm import Mappable  # base class for mapped objects
    from yorm import Converter, Container  # base class for types


def test_from_top_decorators():
    from yorm import sync  # enables mapping on a class's instance objects
    from yorm import sync_instances  # alias for the class decorator
    from yorm import attr  # alternate API to identify mapped attributes


def test_from_top_functions():
    from yorm import sync  # enables mapping on an instance object
    from yorm import sync_object  # alias for the mapping function
    from yorm import update  # fetch (if necessary) and store a mapped object
    from yorm import update_object  # fetch (optional force) a mapped object
    from yorm import update_file  # store a mapped object


def test_from_nested():
    from yorm.types import Integer
    from yorm.types.standard import String
    from yorm.types.extended import Markdown
    from yorm.types.containers import List
