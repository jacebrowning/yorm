# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned,singleton-comparison

import logging
from unittest.mock import Mock

import pytest
from expecter import expect

import yorm
from yorm import exceptions
from yorm import utilities

log = logging.getLogger(__name__)


@pytest.fixture
def model_class(tmpdir):
    tmpdir.chdir()

    @yorm.sync("data/{self.kind}/{self.key}.yml", auto_create=False)
    class Model:

        def __init__(self, kind, key, **kwargs):
            self.kind = kind
            self.key = key
            assert 0 <= len(kwargs) < 2
            if kwargs:
                assert kwargs == {'test': 'test'}

        def __eq__(self, other):
            return (self.kind, self.key) == (other.kind, other.key)

    return Model


@pytest.fixture
def instance(model_class):
    return model_class('foo', 'bar')


@pytest.fixture
def instances(model_class):
    instances = [
        model_class(kind, key)
        for kind in ('spam', 'egg')
        for key in ('foo', 'bar')
    ]
    for instance in instances:
        instance.__mapper__.create()

    return instances


def describe_create():

    def it_creates_files(model_class):
        instance = utilities.create(model_class, 'foo', 'bar')

        expect(instance.__mapper__.exists) == True
        expect(instance.__mapper__.modified) == False

    def it_requires_files_to_not_yet_exist(model_class, instance):
        instance.__mapper__.create()

        with expect.raises(exceptions.DuplicateMappingError):
            utilities.create(model_class, 'foo', 'bar')

    def it_can_overwrite_files(model_class, instance):
        instance.__mapper__.create()

        utilities.create(model_class, 'foo', 'bar', overwrite=True)

    def it_supports_keyword_arguments(model_class):
        instance = utilities.create(model_class, 'foo', key='bar')

        expect(instance.__mapper__.exists) == True

    def it_can_also_be_called_with_an_instance(instance):
        expect(yorm.create(instance)) == instance

    def it_requires_a_mapped_class_or_instance():
        with expect.raises(TypeError):
            utilities.create(Mock)


def describe_find():

    def it_returns_object_when_found(model_class, instance):
        instance.__mapper__.create()

        expect(utilities.find(model_class, 'foo', 'bar')) == instance

    def it_returns_none_when_no_match(model_class):
        expect(utilities.find(model_class, 'not', 'here')) == None

    def it_allows_objects_to_be_created(model_class):
        expect(utilities.find(model_class, 'new', 'one', create=True)) == \
            model_class('new', 'one')

    def it_supports_keyword_arguments(model_class, instance):
        instance.__mapper__.create()

        expect(utilities.find(model_class, 'foo', key='bar')) == instance

    def it_can_also_be_called_with_an_instance(instance):
        expect(yorm.find(instance, create=True)) == instance

    def it_requires_a_mapped_class_or_instance():
        with expect.raises(TypeError):
            utilities.find(Mock)


def describe_match():

    def with_class_and_factory(model_class, instances):
        matches = list(
            utilities.match(
                model_class,
                (lambda key, kind: model_class(kind, key, test="test")),
                kind='spam',
                key='foo',
            )
        )
        expect(len(matches)) == 1
        instance = matches[0]
        expect(instance.kind) == 'spam'
        expect(instance.key) == 'foo'
        expect(instances).contains(instance)

    def with_class_and_no_factory(model_class, instances):
        matches = list(
            utilities.match(
                model_class,
                kind='spam',
                key='foo',
            )
        )
        expect(len(matches)) == 1
        instance = matches[0]
        expect(instance.kind) == 'spam'
        expect(instance.key) == 'foo'
        expect(instances).contains(instance)

    def with_string(model_class, instances):
        matches = list(
            utilities.match(
                "data/{kind}/{key}.yml",
                (lambda key, kind: model_class(kind, key, test="test")),
                kind='egg',
                key='foo',
            )
        )
        expect(len(matches)) == 1
        instance = matches[0]
        expect(instance.kind) == 'egg'
        expect(instance.key) == 'foo'
        expect(instances).contains(instance)

    def with_self_string(model_class, instances):
        matches = list(
            utilities.match(
                "data/{self.kind}/{self.key}.yml",
                (lambda key, kind: model_class(kind, key, test="test")),
                kind='spam',
                key='bar',
            )
        )
        expect(len(matches)) == 1
        instance = matches[0]
        expect(instance.kind) == 'spam'
        expect(instance.key) == 'bar'
        expect(instances).contains(instance)

    def with_class_and_partial_match(model_class, instances):
        matches = list(
            utilities.match(
                model_class,
                kind='spam',
            )
        )
        expect(len(matches)) == 2
        for instance in matches:
            expect(instance.kind) == 'spam'
            expect(instances).contains(instance)

    def with_string_and_partial_match(model_class, instances):
        matches = list(
            utilities.match(
                "data/{kind}/{key}.yml",
                (lambda key, kind: model_class(kind, key, test="test")),
                key='foo',
            )
        )
        expect(len(matches)) == 2
        for instance in matches:
            expect(instance.key) == 'foo'
            expect(instances).contains(instance)

    def with_self_string_and_partial_match(model_class, instances):
        matches = list(
            utilities.match(
                "data/{self.kind}/{self.key}.yml",
                (lambda key, kind: model_class(kind, key, test="test")),
                kind='egg',
            )
        )
        expect(len(matches)) == 2
        for instance in matches:
            expect(instance.kind) == 'egg'
            expect(instances).contains(instance)


def describe_load():

    def it_marks_files_as_unmodified(instance):
        instance.__mapper__.create()
        instance.__mapper__.modified = True

        utilities.load(instance)

        expect(instance.__mapper__.modified) == False

    def it_requires_a_mapped_instance():
        with expect.raises(TypeError):
            utilities.load(Mock)


def describe_save():

    def it_creates_files(instance):
        utilities.save(instance)

        expect(instance.__mapper__.exists) == True

    def it_marks_files_as_modified(instance):
        instance.__mapper__.create()
        instance.__mapper__.modified = False

        utilities.save(instance)

        expect(instance.__mapper__.modified) == True

    def it_expects_the_file_to_not_be_deleted(instance):
        instance.__mapper__.delete()

        with expect.raises(exceptions.DeletedFileError):
            utilities.save(instance)

    def it_requires_a_mapped_instance():
        with expect.raises(TypeError):
            utilities.save(Mock)


def describe_delete():

    def it_deletes_files(instance):
        utilities.delete(instance)

        expect(instance.__mapper__.exists) == False
        expect(instance.__mapper__.deleted) == True

    def it_requires_a_mapped_instance():
        with expect.raises(TypeError):
            utilities.delete(Mock)
