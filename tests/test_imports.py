"""Integration tests for the package namespace."""

# pylint: disable=missing-docstring,no-self-use,unused-variable,unused-import


def test_top():
    import yorm
    assert yorm.bases
    assert yorm.types.Integer
    assert yorm.types.extended.Markdown


def test_from_top_constants():
    from yorm import UUID


def test_from_top_clases():
    from yorm import Mappable
    from yorm import Converter, Container
    from yorm import ModelMixin


def test_from_top_decorators():
    from yorm import sync
    from yorm import sync_instances
    from yorm import sync_object
    from yorm import attr


def test_from_top_utilities():
    from yorm import create
    from yorm import find
    from yorm import match
    from yorm import load
    from yorm import save
    from yorm import delete


def test_from_nested():
    from yorm.types import Integer, Number
    from yorm.types.standard import String
    from yorm.types.extended import Markdown
    from yorm.types.containers import List
