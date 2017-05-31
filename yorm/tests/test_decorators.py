# pylint: disable=unused-variable,unused-argument,expression-not-assigned
# pylint: disable=missing-docstring,no-self-use,no-member,misplaced-comparison-constant

import logging
from unittest.mock import patch, Mock

import pytest
from expecter import expect

from yorm import decorators
from yorm.bases import Converter

log = logging.getLogger(__name__)


class MockConverter(Converter):
    """Sample converter class."""

    @classmethod
    def create_default(cls):
        return None

    @classmethod
    def to_value(cls, data):
        return None

    @classmethod
    def to_data(cls, value):
        return None


def describe_sync():

    def describe_object():

        @pytest.fixture
        def instance():
            cls = type('Sample', (), {})
            instance = cls()
            return instance

        @pytest.fixture
        def path(tmpdir):
            tmpdir.chdir()
            return "sample.yml"

        def with_no_attrs(instance, path):
            sample = decorators.sync(instance, path)

            expect(sample.__mapper__.path) == "sample.yml"
            expect(sample.__mapper__.attrs) == {}

        def with_attrs(instance, path):
            attrs = {'var1': MockConverter}
            sample = decorators.sync(instance, path, attrs)

            expect(sample.__mapper__.path) == "sample.yml"
            expect(sample.__mapper__.attrs) == {'var1': MockConverter}

        def cannot_be_called_twice(instance, path):
            sample = decorators.sync(instance, path)

            with pytest.raises(TypeError):
                decorators.sync(instance, path)

        @patch('yorm.diskutils.exists', Mock(return_value=True))
        @patch('yorm.diskutils.read', Mock(return_value="abc: 123"))
        @patch('yorm.diskutils.stamp', Mock())
        def reads_existing_files(instance, path):
            sample = decorators.sync(instance, path, auto_track=True)

            expect(sample.abc) == 123


@patch('yorm.diskutils.write', Mock())
@patch('yorm.diskutils.stamp', Mock())
@patch('yorm.diskutils.read', Mock(return_value=""))
class TestSyncInstances:
    """Unit tests for the `sync_instances` decorator."""

    @decorators.sync("sample.yml")
    class SampleDecorated:
        """Sample decorated class."""

        def __repr__(self):
            return "<decorated {}>".format(id(self))

    @decorators.sync("sample.yml", auto_track=True)
    class SampleDecoratedAutoTrack:
        """Sample decorated class with automatic attribute tracking."""

        def __repr__(self):
            return "<decorated {}>".format(id(self))

    @decorators.sync("{UUID}.yml")
    class SampleDecoratedIdentifiers:
        """Sample decorated class using UUIDs for paths."""

        def __repr__(self):
            return "<decorated w/ UUID {}>".format(id(self))

    @decorators.sync("tmp/path/to/{n}.yml", {'n': 'name'})
    class SampleDecoratedAttributes:
        """Sample decorated class using an attribute value for paths."""

        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return "<decorated w/ specified attributes {}>".format(id(self))

    @decorators.sync("tmp/path/to/{self.name}.yml")
    class SampleDecoratedAttributesAutomatic:
        """Sample decorated class using an attribute value for paths."""

        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return "<decorated w/ automatic attributes {}>".format(id(self))

    @decorators.sync("{self.a}/{self.b}/{c}.yml", {'self.b': 'b', 'c': 'c'})
    class SampleDecoratedAttributesCombination:
        """Sample decorated class using an attribute value for paths."""

        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c

        def __repr__(self):
            return "<decorated w/ attributes {}>".format(id(self))

    @decorators.sync("sample.yml", attrs={'var1': MockConverter})
    class SampleDecoratedWithAttributes:
        """Sample decorated class using a single path."""

    def test_no_attrs(self):
        """Verify mapping can be enabled with no attributes."""
        sample = self.SampleDecorated()

        expect(sample.__mapper__.path) == "sample.yml"
        expect(sample.__mapper__.attrs) == {}

    def test_with_attrs(self):
        """Verify mapping can be enabled with with attributes."""
        sample = self.SampleDecoratedWithAttributes()
        assert "sample.yml" == sample.__mapper__.path
        assert ['var1'] == list(sample.__mapper__.attrs.keys())

    @patch('yorm.diskutils.exists', Mock(return_value=True))
    def test_init_existing(self):
        """Verify an existing file is read."""
        with patch('yorm.diskutils.read', Mock(return_value="abc: 123")):
            sample = self.SampleDecoratedAutoTrack()
        assert 123 == sample.abc

    @patch('uuid.uuid4', Mock(return_value=Mock(hex='abc123')))
    def test_filename_uuid(self):
        """Verify UUIDs can be used for filename."""
        sample = self.SampleDecoratedIdentifiers()
        assert "abc123.yml" == sample.__mapper__.path
        assert {} == sample.__mapper__.attrs

    def test_filename_attributes(self):
        """Verify attributes can be used to determine filename."""
        sample1 = self.SampleDecoratedAttributes('one')
        sample2 = self.SampleDecoratedAttributes('two')
        assert "tmp/path/to/one.yml" == sample1.__mapper__.path
        assert "tmp/path/to/two.yml" == sample2.__mapper__.path

    def test_filename_attributes_automatic(self):
        """Verify attributes can be used to determine filename (auto save)."""
        sample1 = self.SampleDecoratedAttributesAutomatic('one')
        sample2 = self.SampleDecoratedAttributesAutomatic('two')
        assert "tmp/path/to/one.yml" == sample1.__mapper__.path
        assert "tmp/path/to/two.yml" == sample2.__mapper__.path

    def test_filename_attributes_combination(self):
        """Verify attributes can be used to determine filename (combo)."""
        log.info("Creating first object...")
        sample1 = self.SampleDecoratedAttributesCombination('A', 'B', 'C')
        log.info("Creating second object...")
        sample2 = self.SampleDecoratedAttributesCombination(1, 2, 3)
        assert "A/B/C.yml" == sample1.__mapper__.path
        assert "1/2/3.yml" == sample2.__mapper__.path


def describe_attr():

    class MockConverter1(MockConverter):
        """Sample converter class."""

    class MockConverter2(MockConverter):
        """Sample converter class."""

    @pytest.fixture
    def path(tmpdir):
        tmpdir.chdir()
        return "mock/path"

    def it_accepts_one_argument(path):

        @decorators.attr(var1=MockConverter1)
        @decorators.sync(path)
        class SampleDecoratedSingle:
            """Class using single `attr` decorator."""

        sample = SampleDecoratedSingle()
        expect(sample.__mapper__.attrs) == {'var1': MockConverter1}

    def it_rejects_zero_arguments():
        with expect.raises(ValueError):
            decorators.attr()

    def it_rejects_more_than_one_argument():
        with expect.raises(ValueError):
            decorators.attr(foo=1, bar=2)

    def it_can_be_applied_multiple_times(path):

        @decorators.attr(var1=MockConverter1)
        @decorators.attr(var2=MockConverter2)
        @decorators.sync(path)
        class SampleDecoratedMultiple:
            """Class using multiple `attr` decorators."""

        sample = SampleDecoratedMultiple()
        expect(sample.__mapper__.attrs) == {'var1': MockConverter1,
                                            'var2': MockConverter2}

    def it_can_be_applied_before_sync(path):

        @decorators.attr(var2=MockConverter2)
        @decorators.sync(path, attrs={'var1': MockConverter1})
        class SampleDecoratedCombo:
            """Class using `attr` decorator and providing a mapping."""

        sample = SampleDecoratedCombo()
        expect(sample.__mapper__.attrs) == {'var1': MockConverter1,
                                            'var2': MockConverter2}

    def it_can_be_applied_after_sync(path):

        @decorators.sync(path, attrs={'var1': MockConverter1})
        @decorators.attr(var2=MockConverter2)
        class SampleDecoratedBackwards:
            """Class using `attr` decorator after `sync` decorator."""

        sample = SampleDecoratedBackwards()
        expect(sample.__mapper__.attrs) == {'var1': MockConverter1,
                                            'var2': MockConverter2}
