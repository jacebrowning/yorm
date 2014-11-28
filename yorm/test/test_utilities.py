#!/usr/bin/env python
# pylint:disable=R0201

"""Unit tests for the `utilities` module."""

import pytest
from unittest.mock import patch, Mock

from yorm import common
from yorm import utilities
from yorm.standard import Converter


# sample classes ##############################################################


class MockConverter(Converter):

    """Sample converter class."""

    @classmethod
    def to_value(cls, obj):
        return None

    @classmethod
    def to_data(cls, obj):
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


# tests #######################################################################


@patch('yorm.common.write_text', Mock())
class TestStore:

    """Unit tests for the `store` function."""

    class Sample:

        """Sample class."""

    def test_no_attrs(self):
        """Verify mapping can be enabled with no attributes."""
        sample = utilities.store(self.Sample(), "sample.yml")
        assert "sample.yml" == sample.yorm_path
        assert {} == sample.yorm_attrs

    def test_with_attrs(self):
        """Verify mapping can be enabled with with attributes."""
        mapping = {'var1': MockConverter}
        sample = utilities.store(self.Sample(), "sample.yml", mapping)
        assert "sample.yml" == sample.yorm_path
        assert {'var1': MockConverter} == sample.yorm_attrs

    def test_multiple(self):
        """Verify mapping cannot be enabled twice."""
        sample = utilities.store(self.Sample(), "sample.yml")
        with pytest.raises(common.UseageError):
            utilities.store(sample, "sample.yml")

    @patch('os.path.exists', Mock(return_value=True))
    @patch('yorm.common.read_text', Mock(return_value="abc: 123"))
    def test_init_existing(self):
        """Verify an existing file is read."""
        sample = utilities.store(self.Sample(), "sample.yml")
        assert 123 == sample.abc

    def test_store(self):
        """Verify store is called when setting an attribute."""
        mapping = {'var1': MockConverter}
        sample = utilities.store(self.Sample(), "sample.yml", mapping)
        with patch.object(sample, 'yorm_mapper') as mock_yorm_mapper:
            setattr(sample, 'var1', None)
        mock_yorm_mapper.retrieve.assert_never_called()
        mock_yorm_mapper.store.assert_called_once_with(sample)

    def test_retrieve(self):
        """Verify retrieve is called when getting an attribute."""
        mapping = {'var1': MockConverter}
        sample = utilities.store(self.Sample(), "sample.yml", mapping)
        with patch.object(sample, 'yorm_mapper') as mock_yorm_mapper:
            getattr(sample, 'var1', None)
        mock_yorm_mapper.retrieve.assert_called_once_with(sample)
        mock_yorm_mapper.store.assert_never_called()


@patch('yorm.common.create_dirname', Mock())
@patch('yorm.common.write_text', Mock())
class TestStoreInstances:

    """Unit tests for the `store_instances` decorator."""

    @utilities.store_instances("sample.yml")
    class SampleDecorated:

        """Sample decorated class using a single path."""

    @utilities.store_instances("{UUID}.yml")
    class SampleDecoratedIdentifiers:

        """Sample decorated class using UUIDs for paths."""

    @utilities.store_instances("path/to/{n}.yml", {'n': 'name'})
    class SampleDecoratedAttributes:

        """Sample decorated class using an attribute value for paths."""

        def __init__(self, name):
            self.name = name

    @utilities.store_instances("path/to/{self.name}.yml")
    class SampleDecoratedAttributesAutomatic:

        """Sample decorated class using an attribute value for paths."""

        def __init__(self, name):
            self.name = name

    @utilities.store_instances("{self.a}/{self.b}/{c}.yml",
                               {'self.b': 'b', 'c': 'c'})
    class SampleDecoratedAttributesCombination:

        """Sample decorated class using an attribute value for paths."""

        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c

    @utilities.store_instances("sample.yml", mapping={'var1': MockConverter})
    class SampleDecoratedWithAttributes:

        """Sample decorated class using a single path."""

    def test_no_attrs(self):
        """Verify mapping can be enabled with no attributes."""
        sample = self.SampleDecorated()
        assert "sample.yml" == sample.yorm_path
        assert {} == sample.yorm_attrs

    def test_with_attrs(self):
        """Verify mapping can be enabled with with attributes."""
        sample = self.SampleDecoratedWithAttributes()
        assert "sample.yml" == sample.yorm_path
        assert ['var1'] == list(sample.yorm_attrs.keys())

    @patch('os.path.exists', Mock(return_value=True))
    @patch('yorm.common.read_text', Mock(return_value="abc: 123"))
    def test_init_existing(self):
        """Verify an existing file is read."""
        sample = self.SampleDecorated()
        assert 123 == sample.abc

    @patch('uuid.uuid4', Mock(return_value=Mock(hex='abc123')))
    def test_filename_uuid(self):
        """Verify UUIDs can be used for filename."""
        sample = self.SampleDecoratedIdentifiers()
        assert "abc123.yml" == sample.yorm_path
        assert {} == sample.yorm_attrs

    def test_filename_attributes(self):
        """Verify attributes can be used to determine filename."""
        sample1 = self.SampleDecoratedAttributes('one')
        sample2 = self.SampleDecoratedAttributes('two')
        assert "path/to/one.yml" == sample1.yorm_path
        assert "path/to/two.yml" == sample2.yorm_path

    def test_filename_attributes_automatic(self):
        """Verify attributes can be used to determine filename (auto)."""
        sample1 = self.SampleDecoratedAttributesAutomatic('one')
        sample2 = self.SampleDecoratedAttributesAutomatic('two')
        assert "path/to/one.yml" == sample1.yorm_path
        assert "path/to/two.yml" == sample2.yorm_path

    def test_filename_attributes_combination(self):
        """Verify attributes can be used to determine filename (combo)."""
        sample1 = self.SampleDecoratedAttributesCombination('A', 'B', 'C')
        sample2 = self.SampleDecoratedAttributesCombination(1, 2, 3)
        assert "A/B/C.yml" == sample1.yorm_path
        assert "1/2/3.yml" == sample2.yorm_path

    def test_store(self):
        """Verify store is called when setting an attribute."""
        sample = self.SampleDecoratedWithAttributes()
        with patch.object(sample, 'yorm_mapper') as mock_yorm_mapper:
            setattr(sample, 'var1', None)
        mock_yorm_mapper.retrieve.assert_never_called()
        mock_yorm_mapper.store.assert_called_once_with(sample)

    def test_retrieve(self):
        """Verify retrieve is called when getting an attribute."""
        sample = self.SampleDecoratedWithAttributes()
        with patch.object(sample, 'yorm_mapper') as mock_yorm_mapper:
            getattr(sample, 'var1', None)
        mock_yorm_mapper.retrieve.assert_called_once_with(sample)
        mock_yorm_mapper.store.assert_never_called()


@patch('yorm.common.write_text', Mock())
class TestMapAttr:

    """Unit tests for the `map_attr` decorator."""

    @utilities.map_attr(var1=MockConverter1, var2=MockConverter2)
    @utilities.store_instances("sample.yml")
    class SampleDecoratedSingle:

        """Sample decorated class using one `map_attr` decorator."""

    @utilities.map_attr()
    @utilities.map_attr(var1=MockConverter1)
    @utilities.map_attr(var2=MockConverter2, var3=MockConverter3)
    @utilities.store_instances("sample.yml")
    class SampleDecoratedMultiple:

        """Sample decorated class using many `map_attr` decorators."""

    @utilities.map_attr()
    @utilities.map_attr(var1=MockConverter1)
    @utilities.map_attr(var2=MockConverter2, var3=MockConverter3)
    @utilities.store_instances("sample.yml", mapping={'var0': MockConverter0})
    class SampleDecoratedCombo:

        """Sample decorated class using `map_attr` and providing a mapping."""

    @utilities.store_instances("sample.yml", mapping={'var0': MockConverter0})
    @utilities.map_attr(var1=MockConverter1)
    class SampleDecoratedBackwards:

        """Sample decorated class using one `map_attr` decorator."""

    def test_single(self):
        """Verify `map_attr` can be applied once."""
        sample = self.SampleDecoratedSingle()
        expected = {'var1': MockConverter1,
                    'var2': MockConverter2}
        assert expected == sample.yorm_attrs

    def test_multiple(self):
        """Verify `map_attr` can be applied many times."""
        sample = self.SampleDecoratedMultiple()
        expected = {'var1': MockConverter1,
                    'var2': MockConverter2,
                    'var3': MockConverter3}
        assert expected == sample.yorm_attrs

    def test_combo(self):
        """Verify `map_attr` can be applied an existing mapping."""
        sample = self.SampleDecoratedCombo()
        expected = {'var0': MockConverter0,
                    'var1': MockConverter1,
                    'var2': MockConverter2,
                    'var3': MockConverter3}
        assert expected == sample.yorm_attrs

    def test_backwards(self):
        """Verify `map_attr` can be applied before `store_instances`."""
        sample = self.SampleDecoratedBackwards()
        expected = {'var0': MockConverter0,
                    'var1': MockConverter1}
        assert expected == sample.yorm_attrs


if __name__ == '__main__':
    pytest.main()
