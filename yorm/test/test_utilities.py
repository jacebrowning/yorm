# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned

import logging
from unittest.mock import Mock

import pytest

from yorm import exceptions
from yorm import utilities

log = logging.getLogger(__name__)


@pytest.fixture
def instance():
    obj = Mock()
    obj.__mapper__ = Mock()
    obj.__mapper__.attrs = {}
    obj.__mapper__.reset_mock()
    return obj


def describe_update():

    def it_fetches_and_stores(instance):
        utilities.update(instance)

        assert instance.__mapper__.fetch.called
        assert instance.__mapper__.store.called

    def it_only_stores_when_requested(instance):
        utilities.update(instance, store=False)

        assert instance.__mapper__.fetch.called
        assert not instance.__mapper__.store.called

    def it_only_fetches_when_requested(instance):
        utilities.update(instance, fetch=False)

        assert not instance.__mapper__.fetch.called
        assert instance.__mapper__.store.called

    def it_raises_an_exception_with_the_wrong_base():
        instance = Mock()

        with pytest.raises(exceptions.MappingError):
            utilities.update(instance)


def describe_update_object():

    def it_fetches(instance):
        utilities.update_object(instance)

        assert instance.__mapper__.fetch.called
        assert not instance.__mapper__.store.called

    def it_raises_an_exception_with_the_wrong_base():
        instance = Mock()

        with pytest.raises(exceptions.MappingError):
            utilities.update_object(instance)


def describe_update_file():

    def it_stores(instance):
        utilities.update_file(instance)

        assert False is instance.__mapper__.fetch.called
        assert True is instance.__mapper__.store.called

    def it_raises_an_exception_with_the_wrong_base():
        instance = Mock()

        with pytest.raises(exceptions.MappingError):
            utilities.update_file(instance)

    def it_only_stores_with_auto_on(instance):
        instance.__mapper__.auto = False

        utilities.update_file(instance, force=False)

        assert False is instance.__mapper__.fetch.called
        assert False is instance.__mapper__.store.called

    def it_creates_missing_files(instance):
        instance.__mapper__.exists = False

        utilities.update_file(instance)

        assert False is instance.__mapper__.fetch.called
        assert True is instance.__mapper__.create.called
        assert True is instance.__mapper__.store.called
