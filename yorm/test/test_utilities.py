#!/usr/bin/env python
# pylint:disable=R0201

"""Unit tests for the `utilities` module."""

import pytest
from unittest.mock import patch, Mock

from yorm import exceptions
from yorm import utilities
from yorm.bases import Converter, Mappable


class MockConverter(Converter):

    """Sample converter class."""

    @classmethod
    def create_default(cls):
        return None

    @classmethod
    def to_value(cls, _):
        return None

    @classmethod
    def to_data(cls, _):
        return None


class MockConverter0(MockConverter):

    """Sample converter class."""


class MockConverter1(MockConverter):

    """Sample converter class."""


class MockConverter2(MockConverter):

    """Sample converter class."""


class MockConverter3(MockConverter):

    """Sample converter class."""


class MockConverter4(MockConverter):

    """Sample converter class."""


class MockMappable(Mappable):

    """Sample mappable class."""

    yorm_mapper = Mock()
    yorm_mapper.attrs = {}


@patch('yorm.common.write_text', Mock())
@patch('yorm.common.stamp', Mock())
@patch('yorm.common.read_text', Mock(return_value=""))
class TestSyncObject:

    """Unit tests for the `sync_object` function."""

    class Sample:

        """Sample class."""

    def test_no_attrs(self):
        """Verify mapping can be enabled with no attributes."""
        sample = utilities.sync(self.Sample(), "sample.yml")
        assert "sample.yml" == sample.yorm_mapper.path
        assert {} == sample.yorm_mapper.attrs

    def test_with_attrs(self):
        """Verify mapping can be enabled with with attributes."""
        attrs = {'var1': MockConverter}
        sample = utilities.sync(self.Sample(), "sample.yml", attrs)
        assert "sample.yml" == sample.yorm_mapper.path
        assert {'var1': MockConverter} == sample.yorm_mapper.attrs

    def test_multiple(self):
        """Verify mapping cannot be enabled twice."""
        sample = utilities.sync(self.Sample(), "sample.yml")
        with pytest.raises(exceptions.MappingError):
            utilities.sync(sample, "sample.yml")

    @patch('os.path.isfile', Mock(return_value=True))
    def test_init_existing(self):
        """Verify an existing file is read."""
        with patch('yorm.common.read_text', Mock(return_value="abc: 123")):
            sample = utilities.sync(self.Sample(), "sample.yml")
        assert 123 == sample.abc

    @patch('os.path.isfile', Mock(return_value=False))
    def test_exception_when_file_expected_but_missing(self):
        utilities.sync(self.Sample(), "sample.yml", existing=False)
        with pytest.raises(exceptions.FileMissingError):
            utilities.sync(self.Sample(), "sample.yml", existing=True)

    @patch('os.path.isfile', Mock(return_value=True))
    def test_exception_when_file_not_expected_but_found(self):
        utilities.sync(self.Sample(), "sample.yml", existing=True)
        with pytest.raises(exceptions.FileAlreadyExistsError):
            utilities.sync(self.Sample(), "sample.yml", existing=False)


@patch('yorm.common.create_dirname', Mock())
@patch('yorm.common.write_text', Mock())
@patch('yorm.common.stamp', Mock())
@patch('yorm.common.read_text', Mock(return_value=""))
class TestSyncInstances:

    """Unit tests for the `sync_instances` decorator."""

    @utilities.sync("sample.yml")
    class SampleDecorated:

        """Sample decorated class using a single path."""

        def __repr__(self):
            return "<decorated {}>".format(id(self))

    @utilities.sync("{UUID}.yml")
    class SampleDecoratedIdentifiers:

        """Sample decorated class using UUIDs for paths."""

        def __repr__(self):
            return "<decorated w/ UUID {}>".format(id(self))

    @utilities.sync("path/to/{n}.yml", {'n': 'name'})
    class SampleDecoratedAttributes:

        """Sample decorated class using an attribute value for paths."""

        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return "<decorated w/ specified attributes {}>".format(id(self))

    @utilities.sync("path/to/{self.name}.yml")
    class SampleDecoratedAttributesAutomatic:

        """Sample decorated class using an attribute value for paths."""

        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return "<decorated w/ automatic attributes {}>".format(id(self))

    @utilities.sync("{self.a}/{self.b}/{c}.yml", {'self.b': 'b', 'c': 'c'})
    class SampleDecoratedAttributesCombination:

        """Sample decorated class using an attribute value for paths."""

        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c

        def __repr__(self):
            return "<decorated w/ attributes {}>".format(id(self))

    @utilities.sync("sample.yml", attrs={'var1': MockConverter})
    class SampleDecoratedWithAttributes:

        """Sample decorated class using a single path."""

    @utilities.sync("sample.yml", attrs={'var1': MockConverter}, auto=False)
    class SampleDecoratedWithAttributesAutoOff:

        """Sample decorated class using a single path."""

    def test_no_attrs(self):
        """Verify mapping can be enabled with no attributes."""
        sample = self.SampleDecorated()
        assert "sample.yml" == sample.yorm_mapper.path
        assert {} == sample.yorm_mapper.attrs

    def test_with_attrs(self):
        """Verify mapping can be enabled with with attributes."""
        sample = self.SampleDecoratedWithAttributes()
        assert "sample.yml" == sample.yorm_mapper.path
        assert ['var1'] == list(sample.yorm_mapper.attrs.keys())

    @patch('os.path.isfile', Mock(return_value=True))
    def test_init_existing(self):
        """Verify an existing file is read."""
        with patch('yorm.common.read_text', Mock(return_value="abc: 123")):
            sample = self.SampleDecorated()
        assert 123 == sample.abc

    @patch('uuid.uuid4', Mock(return_value=Mock(hex='abc123')))
    def test_filename_uuid(self):
        """Verify UUIDs can be used for filename."""
        sample = self.SampleDecoratedIdentifiers()
        assert "abc123.yml" == sample.yorm_mapper.path
        assert {} == sample.yorm_mapper.attrs

    def test_filename_attributes(self):
        """Verify attributes can be used to determine filename."""
        sample1 = self.SampleDecoratedAttributes('one')
        sample2 = self.SampleDecoratedAttributes('two')
        assert "path/to/one.yml" == sample1.yorm_mapper.path
        assert "path/to/two.yml" == sample2.yorm_mapper.path

    def test_filename_attributes_automatic(self):
        """Verify attributes can be used to determine filename (auto)."""
        sample1 = self.SampleDecoratedAttributesAutomatic('one')
        sample2 = self.SampleDecoratedAttributesAutomatic('two')
        assert "path/to/one.yml" == sample1.yorm_mapper.path
        assert "path/to/two.yml" == sample2.yorm_mapper.path

    def test_filename_attributes_combination(self):
        """Verify attributes can be used to determine filename (combo)."""
        sample1 = self.SampleDecoratedAttributesCombination('A', 'B', 'C')
        sample2 = self.SampleDecoratedAttributesCombination(1, 2, 3)
        assert "A/B/C.yml" == sample1.yorm_mapper.path
        assert "1/2/3.yml" == sample2.yorm_mapper.path


@patch('yorm.common.write_text', Mock())
@patch('yorm.common.stamp', Mock())
@patch('yorm.common.read_text', Mock(return_value=""))
class TestAttr:

    """Unit tests for the `attr` decorator."""

    @utilities.attr(var1=MockConverter1, var2=MockConverter2)
    @utilities.sync("sample.yml")
    class SampleDecoratedSingle:

        """Sample decorated class using one `attr` decorator."""

    @utilities.attr()
    @utilities.attr(var1=MockConverter1)
    @utilities.attr(var2=MockConverter2, var3=MockConverter3)
    @utilities.sync("sample.yml")
    class SampleDecoratedMultiple:

        """Sample decorated class using many `attr` decorators."""

    @utilities.attr()
    @utilities.attr(var1=MockConverter1)
    @utilities.attr(var2=MockConverter2, var3=MockConverter3)
    @utilities.sync("sample.yml", attrs={'var0': MockConverter0})
    class SampleDecoratedCombo:

        """Sample decorated class using `attr` and providing a mapping."""

    @utilities.sync("sample.yml", attrs={'var0': MockConverter0})
    @utilities.attr(var1=MockConverter1)
    class SampleDecoratedBackwards:

        """Sample decorated class using one `attr` decorator."""

    def test_single(self):
        """Verify `attr` can be applied once."""
        sample = self.SampleDecoratedSingle()
        expected = {'var1': MockConverter1,
                    'var2': MockConverter2}
        assert expected == sample.yorm_mapper.attrs

    def test_multiple(self):
        """Verify `attr` can be applied many times."""
        sample = self.SampleDecoratedMultiple()
        expected = {'var1': MockConverter1,
                    'var2': MockConverter2,
                    'var3': MockConverter3}
        assert expected == sample.yorm_mapper.attrs

    def test_combo(self):
        """Verify `attr` can be applied an existing mapping."""
        sample = self.SampleDecoratedCombo()
        expected = {'var0': MockConverter0,
                    'var1': MockConverter1,
                    'var2': MockConverter2,
                    'var3': MockConverter3}
        assert expected == sample.yorm_mapper.attrs

    def test_backwards(self):
        """Verify `attr` can be applied before `sync`."""
        sample = self.SampleDecoratedBackwards()
        expected = {'var0': MockConverter0,
                    'var1': MockConverter1}
        assert expected == sample.yorm_mapper.attrs


class TestUpdate:

    """Unit tests for the `update` function."""

    def test_update(self):
        """Verify the object and file are updated."""
        instance = MockMappable()
        instance.yorm_mapper.reset_mock()

        utilities.update(instance)

        assert instance.yorm_mapper.fetch.called
        assert instance.yorm_mapper.store.called

    def test_update_object_only(self):
        """Verify only the object is updated."""
        instance = MockMappable()
        instance.yorm_mapper.reset_mock()

        utilities.update(instance, store=False)

        assert instance.yorm_mapper.fetch.called
        assert not instance.yorm_mapper.store.called

    def test_update_file_only(self):
        """Verify only the file is updated."""
        instance = MockMappable()
        instance.yorm_mapper.reset_mock()

        utilities.update(instance, fetch=False)

        assert not instance.yorm_mapper.fetch.called
        assert instance.yorm_mapper.store.called

    def test_update_wrong_base(self):
        """Verify an exception is raised with the wrong base."""
        instance = Mock()

        with pytest.raises(exceptions.MappingError):
            utilities.update(instance)


class TestUpdateObject:

    """Unit tests for the `update_object` function."""

    def test_update(self):
        """Verify only the object is updated."""
        instance = MockMappable()
        instance.yorm_mapper.reset_mock()

        utilities.update_object(instance)

        assert instance.yorm_mapper.fetch.called
        assert not instance.yorm_mapper.store.called

    def test_update_wrong_base(self):
        """Verify an exception is raised with the wrong base."""
        instance = Mock()

        with pytest.raises(exceptions.MappingError):
            utilities.update_object(instance)


class TestUpdateFile:

    """Unit tests for the `update_file` function."""

    def test_update(self):
        """Verify only the file is updated."""
        instance = MockMappable()
        instance.yorm_mapper.reset_mock()

        utilities.update_file(instance)

        assert False is instance.yorm_mapper.fetch.called
        assert False is instance.yorm_mapper.create.called
        assert True is instance.yorm_mapper.store.called

    def test_update_wrong_base(self):
        """Verify an exception is raised with the wrong base."""
        instance = Mock()

        with pytest.raises(exceptions.MappingError):
            utilities.update_file(instance)

    def test_store_not_called_with_auto_off(self):
        instance = MockMappable()
        instance.yorm_mapper.reset_mock()
        instance.yorm_mapper.auto = False

        utilities.update_file(instance, force=False)

        assert False is instance.yorm_mapper.fetch.called
        assert False is instance.yorm_mapper.create.called
        assert False is instance.yorm_mapper.store.called

    def test_create_called_if_the_file_is_missing(self):
        instance = MockMappable()
        instance.yorm_mapper.reset_mock()
        instance.yorm_mapper.exists = False

        utilities.update_file(instance)

        assert False is instance.yorm_mapper.fetch.called
        assert True is instance.yorm_mapper.create.called
        assert True is instance.yorm_mapper.store.called


if __name__ == '__main__':
    pytest.main()
