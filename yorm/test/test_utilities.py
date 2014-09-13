#!/usr/bin/env python
# pylint:disable=R0201

"""Unit tests for the `utilities` module."""

import pytest
from unittest.mock import patch, Mock

from yorm import utilities


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
        mapping = {'var1': 'Mock'}
        sample = utilities.store(self.Sample(), "sample.yml", mapping)
        assert "sample.yml" == sample.yorm_path
        assert {'var1': 'Mock'} == sample.yorm_attrs

    def test_store(self):
        """Verify store is called when setting an attribute."""
        mapping = {'var1': 'Mock'}
        sample = utilities.store(self.Sample(), "sample.yml", mapping)
        with patch.object(sample, 'yorm_mapper') as mock_yorm_mapper:
            setattr(sample, 'var1', None)
        mock_yorm_mapper.retrieve.assert_never_called()
        mock_yorm_mapper.store.assert_called_once_with(sample)

    def test_retrieve(self):
        """Verify retrieve is called when getting an attribute."""
        mapping = {'var1': 'Mock'}
        sample = utilities.store(self.Sample(), "sample.yml", mapping)
        with patch.object(sample, 'yorm_mapper') as mock_yorm_mapper:
            getattr(sample, 'var1', None)
        mock_yorm_mapper.retrieve.assert_called_once_with(sample)
        mock_yorm_mapper.store.assert_never_called()


@patch('yorm.common.write_text', Mock())
class TestStoreInstances:

    """Unit tests for the `store_instances` decorator."""

    @utilities.store_instances("sample.yml")
    class SampleDecorated:

        """Sample decorated class using a single path."""

    @utilities.store_instances("{UUID}.yml")
    class SampleDecoratedIdentifiers:

        """Sample decorated class using UUIDs for paths."""

    @utilities.store_instances("sample.yml", mapping={'var1': 'Mock'})
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
        assert {'var1': 'Mock'} == sample.yorm_attrs

    @patch('uuid.uuid4', Mock(return_value=Mock(hex='abc123')))
    def test_uuid(self):
        """Verify UUIDs can be used for filename."""
        sample = self.SampleDecoratedIdentifiers()
        assert "abc123.yml" == sample.yorm_path
        assert {} == sample.yorm_attrs

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

    @utilities.map_attr(var1='Var1', var2='Var2')
    @utilities.store_instances("sample.yml")
    class SampleDecoratedSingle:

        """Sample decorated class using one `map_attr` decorator."""

    @utilities.map_attr()
    @utilities.map_attr(var1='Var1')
    @utilities.map_attr(var2='Var2', var3='Var3')
    @utilities.store_instances("sample.yml")
    class SampleDecoratedMultiple:

        """Sample decorated class using many `map_attr` decorators."""

    @utilities.map_attr()
    @utilities.map_attr(var1='Var1')
    @utilities.map_attr(var2='Var2', var3='Var3')
    @utilities.store_instances("sample.yml", mapping={'var0': 'Var0'})
    class SampleDecoratedCombo:

        """Sample decorated class using `map_attr` and providing a mapping."""

    @utilities.store_instances("sample.yml", mapping={'var0': 'Var0'})
    @utilities.map_attr(var1='Var1')
    class SampleDecoratedBackwards:

        """Sample decorated class using one `map_attr` decorator."""

    def test_single(self):
        """Verify `map_attr` can be applied once."""
        sample = self.SampleDecoratedSingle()
        expected = {'var1': 'Var1',
                    'var2': 'Var2'}
        assert expected == sample.yorm_attrs

    def test_multiple(self):
        """Verify `map_attr` can be applied many times."""
        sample = self.SampleDecoratedMultiple()
        expected = {'var1': 'Var1',
                    'var2': 'Var2',
                    'var3': 'Var3'}
        assert expected == sample.yorm_attrs

    def test_combo(self):
        """Verify `map_attr` can be applied an existing mapping."""
        sample = self.SampleDecoratedCombo()
        expected = {'var0': 'Var0',
                    'var1': 'Var1',
                    'var2': 'Var2',
                    'var3': 'Var3'}
        assert expected == sample.yorm_attrs

    def test_backwards(self):
        """Verify `map_attr` can be applied before `store_instances`."""
        sample = self.SampleDecoratedBackwards()
        expected = {'var0': 'Var0',
                    'var1': 'Var1'}
        assert expected == sample.yorm_attrs


if __name__ == '__main__':
    pytest.main()
