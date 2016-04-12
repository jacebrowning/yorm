# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned,singleton-comparison

import logging

import pytest
from expecter import expect

import yorm
from yorm import exceptions
from yorm import utilities

log = logging.getLogger(__name__)


@pytest.fixture
def model_class(tmpdir):
    tmpdir.chdir()

    @yorm.sync("data/{self.kind}/{self.key}.yml", auto=False)
    class Model:

        def __init__(self, kind, key):
            self.kind = kind
            self.key = key

        def __eq__(self, other):
            return (self.kind, self.key) == (other.kind, other.key)

    return Model


@pytest.fixture
def instance(model_class):
    return model_class('foo', 'bar')


def describe_new():

    def it_creates_files(instance):
        utilities.new(instance)

        expect(instance.__mapper__.exists) == True

    def it_requires_files_to_not_yet_exist(instance):
        instance.__mapper__.create()

        with expect.raises(exceptions.FileAlreadyExistsError):
            utilities.new(instance)

    def it_requires_a_mapped_object():
        with expect.raises(exceptions.MappingError):
            utilities.new(42)


def describe_find():

    def it_returns_object_when_found(instance):
        instance.__mapper__.create()

        expect(utilities.find(instance)) == instance

    def it_returns_none_when_no_match(instance):
        expect(utilities.find(instance)) == None

    def it_requires_a_mapped_object():
        with expect.raises(exceptions.MappingError):
            utilities.find(42)


def describe_load():

    def it_is_not_yet_implemented():
        with expect.raises(NotImplementedError):
            utilities.load(None)


def describe_save():

    def it_creates_files(instance):
        utilities.save(instance)

        expect(instance.__mapper__.exists) == True

    def it_expects_the_file_to_not_be_deleted(instance):
        instance.__mapper__.delete()

        with expect.raises(exceptions.FileDeletedError):
            utilities.save(instance)

    def it_requires_a_mapped_object():
        with expect.raises(exceptions.MappingError):
            utilities.save(42)


def describe_delete():

    def it_deletes_files(instance):
        utilities.delete(instance)

        expect(instance.__mapper__.exists) == False
        expect(instance.__mapper__.deleted) == True

    def it_requires_a_mapped_object():
        with expect.raises(exceptions.MappingError):
            utilities.delete(42)
