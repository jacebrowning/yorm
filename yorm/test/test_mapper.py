# pylint: disable=missing-docstring,redefined-outer-name,unused-variable,expression-not-assigned

import pytest
from expecter import expect

import yorm
from yorm import exceptions
from yorm.mapper import Mapper
from yorm.types import Integer


class MyObject:
    var1 = 1


@pytest.fixture
def obj():
    return MyObject()


@pytest.fixture
def attrs():
    return {'var2': Integer, 'var3': Integer}


@pytest.fixture
def mapper(tmpdir, obj, attrs):
    tmpdir.chdir()
    return Mapper(obj, "real/path/to/file", attrs)


@pytest.yield_fixture
def mapper_fake(obj, attrs):
    backup = yorm.settings.fake
    yorm.settings.fake = True
    yield Mapper(obj, "fake/path/to/file", attrs)
    yorm.settings.fake = backup


def describe_mapper():

    def describe_create():

        def it_creates_the_file(mapper):
            mapper.create()

            expect(mapper.path).exists()
            expect(mapper.exists).is_true()
            expect(mapper.deleted).is_false()

        def it_pretends_when_fake(mapper_fake):
            mapper_fake.create()

            expect(mapper_fake.path).missing()
            expect(mapper_fake.exists).is_true()
            expect(mapper_fake.deleted).is_false()

        def it_can_be_called_twice(mapper):
            mapper.create()
            mapper.create()  # should be ignored

            expect(mapper.path).exists()

    def describe_delete():

        def it_deletes_the_file(mapper):
            mapper.delete()

            expect(mapper.path).missing()
            expect(mapper.exists).is_false()
            expect(mapper.deleted).is_true()

        def it_pretends_when_fake(mapper_fake):
            mapper_fake.delete()

            expect(mapper_fake.path).missing()
            expect(mapper_fake.exists).is_false()
            expect(mapper_fake.deleted).is_true()

        def it_can_be_called_twice(mapper):
            mapper.delete()
            mapper.delete()  # should be ignored

            expect(mapper.path).missing()

    def describe_fetch():

        def it_adds_missing_attributes(obj, mapper):
            mapper.create()
            mapper.fetch()

            expect(obj.var1) == 1
            expect(obj.var2) == 0
            expect(obj.var3) == 0

        def it_raises_an_exception_after_delete(mapper):
            mapper.delete()

            with expect.raises(exceptions.FileDeletedError):
                mapper.fetch()

    def describe_store():

        def it_creates_the_file_automatically(mapper):
            mapper.store()

            expect(mapper.path).exists()

    def describe_modified():

        def is_true_initially(mapper, mapper_fake):
            expect(mapper.modified).is_true()
            expect(mapper_fake.modified).is_true()

        def is_true_after_create(mapper, mapper_fake):
            mapper.create()
            mapper_fake.create()

            expect(mapper.modified).is_true()
            expect(mapper_fake.modified).is_true()

        def can_be_set_false(mapper, mapper_fake):
            mapper.modified = False
            mapper_fake.modified = False

            expect(mapper.modified).is_false()
            expect(mapper_fake.modified).is_false()

        def can_be_set_true(mapper, mapper_fake):
            mapper.modified = True
            mapper_fake.modified = True

            expect(mapper.modified).is_true()
            expect(mapper_fake.modified).is_true()
