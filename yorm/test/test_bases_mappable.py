# pylint: disable=missing-docstring,no-self-use,attribute-defined-outside-init,protected-access,misplaced-comparison-constant

import logging
from unittest.mock import Mock

import pytest

import yorm
from yorm.bases import Mappable
from yorm.mapper import Mapper
from yorm.types import String, Integer, Boolean, List, Dictionary

from . import strip


class MockMapper(Mapper):
    """Mapped file with stubbed file IO."""

    def __init__(self, obj, path, attrs):
        super().__init__(obj, path, attrs)
        self._mock_file = None
        self._mock_modified = True
        self.exists = True

    def _read(self):
        text = self._mock_file
        logging.debug("Mock read:\n%s", text.strip())
        return text

    def _write(self, text):
        logging.debug("Mock write:\n%s", text.strip())
        self._mock_file = text
        self.modified = True

    @property
    def modified(self):
        return self._mock_modified

    @modified.setter
    def modified(self, changes):
        self._mock_modified = changes


# CLASSES ######################################################################

@yorm.attr(all=Integer)
class IntegerList(List):
    """List of integers."""


@yorm.attr(status=Boolean)
class StatusDictionary(Dictionary):
    """Dictionary of statuses."""


class SampleMappable(Mappable):
    """Sample mappable class with hard-coded settings."""

    def __init__(self):
        self.__mapper__ = None

        logging.debug("Initializing sample...")
        self.var1 = None
        self.var2 = None
        self.var3 = None
        self.var4 = None
        self.var5 = None
        logging.debug("Sample initialized")

        path = "mock/path/to/sample.yml"
        attrs = {'var1': String,
                 'var2': Integer,
                 'var3': Boolean,
                 'var4': IntegerList,
                 'var5': StatusDictionary}
        self.__mapper__ = MockMapper(self, path, attrs)
        self.__mapper__.save()

    def __repr__(self):
        return "<sample {}>".format(id(self))


# TESTS ########################################################################


class TestMappable:
    """Unit tests for the `Mappable` class."""

    def setup_method(self, _):
        """Create an mappable instance for tests."""
        self.sample = SampleMappable()

    def test_init(self):
        """Verify files are created after initialized."""
        text = self.sample.__mapper__._read()
        assert strip("""
        var1: ''
        var2: 0
        var3: false
        var4: []
        var5:
          status: false
        """) == text

    def test_set(self):
        """Verify the file is written to after setting an attribute."""
        self.sample.var1 = "abc123"
        self.sample.var2 = 1
        self.sample.var3 = True
        self.sample.var4 = [42]
        self.sample.var5 = {'status': True}
        text = self.sample.__mapper__._read()
        assert strip("""
        var1: abc123
        var2: 1
        var3: true
        var4:
        - 42
        var5:
          status: true
        """) == text

    def test_set_converted(self):
        """Verify conversion occurs when setting attributes."""
        self.sample.var1 = 42
        self.sample.var2 = "1"
        self.sample.var3 = 'off'
        self.sample.var4 = None
        self.sample.var5 = {'status': 1}
        text = self.sample.__mapper__._read()
        assert strip("""
        var1: 42
        var2: 1
        var3: false
        var4: []
        var5:
          status: true
        """) == text

    def test_set_error(self):
        """Verify an exception is raised when a value cannot be converted."""
        with pytest.raises(ValueError):
            self.sample.var2 = "abc"

    def test_get(self):
        """Verify the file is read from before getting an attribute."""
        text = strip("""
        var1: def456
        var2: 42
        var3: off
        """)
        self.sample.__mapper__._write(text)
        assert"def456" == self.sample.var1
        assert 42 == self.sample.var2
        assert False is self.sample.var3

    def test_error_invalid_yaml(self):
        """Verify an exception is raised on invalid YAML."""
        text = strip("""
        invalid: -
        """)
        self.sample.__mapper__._write(text)
        with pytest.raises(ValueError):
            print(self.sample.var1)

    def test_error_unexpected_yaml(self):
        """Verify an exception is raised on unexpected YAML."""
        text = strip("""
        not a dictionary
        """)
        self.sample.__mapper__._write(text)
        with pytest.raises(ValueError):
            print(self.sample.var1)

    def test_new(self):
        """Verify new attributes are added to the object."""
        self.sample.__mapper__.auto_track = True
        text = strip("""
        new: 42
        """)
        self.sample.__mapper__._write(text)
        assert 42 == self.sample.new

    def test_new_unknown(self):
        """Verify an exception is raised on new attributes w/ unknown types"""
        self.sample.__mapper__.auto_track = True
        text = strip("""
        new: !!timestamp 2001-12-15T02:59:43.1Z
        """)
        self.sample.__mapper__._write(text)
        with pytest.raises(ValueError):
            print(self.sample.var1)


class TestMappableTriggers:

    class MockDict(Mappable, dict):
        pass

    class MockList:

        def append(self, value):
            print(value)

    class Sample(MockDict, MockList):

        __mapper__ = Mock()
        __mapper__.attrs = {}
        __mapper__.load = Mock()
        __mapper__.save = Mock()

    def setup_method(self, _):
        """Create an mappable instance for tests."""
        self.sample = self.Sample()
        self.sample.__mapper__.load.reset_mock()
        self.sample.__mapper__.save.reset_mock()
        self.sample.__mapper__.auto_save_after_load = False

    def test_getattribute(self):
        with pytest.raises(AttributeError):
            getattr(self.sample, 'foo')
        assert 1 == self.sample.__mapper__.load.call_count
        assert 0 == self.sample.__mapper__.save.call_count

    def test_setattr(self):
        self.sample.__mapper__.attrs['foo'] = Mock()
        setattr(self.sample, 'foo', 'bar')
        assert 0 == self.sample.__mapper__.load.call_count
        assert 1 == self.sample.__mapper__.save.call_count

    def test_getitem(self):
        with pytest.raises(KeyError):
            print(self.sample['foo'])
        assert 1 == self.sample.__mapper__.load.call_count
        assert 0 == self.sample.__mapper__.save.call_count

    def test_setitem(self):
        self.sample['foo'] = 'bar'
        assert 0 == self.sample.__mapper__.load.call_count
        assert 1 == self.sample.__mapper__.save.call_count

    def test_delitem(self):
        self.sample['foo'] = 'bar'
        self.sample.__mapper__.save.reset_mock()

        del self.sample['foo']
        assert 0 == self.sample.__mapper__.load.call_count
        assert 1 == self.sample.__mapper__.save.call_count

    def test_append(self):
        self.sample.append('foo')
        assert 1 == self.sample.__mapper__.load.call_count
        assert 1 == self.sample.__mapper__.save.call_count

    def test_iter(self):
        self.sample.append('foo')
        self.sample.append('bar')
        self.sample.__mapper__.load.reset_mock()
        self.sample.__mapper__.save.reset_mock()
        self.sample.__mapper__.auto_save_after_load = False
        self.sample.__mapper__.modified = True

        for item in self.sample:
            print(item)
        assert 1 == self.sample.__mapper__.load.call_count
        assert 0 == self.sample.__mapper__.save.call_count

    def test_handle_missing_mapper(self):
        sample = self.MockDict()
        sample.__mapper__ = None
        sample[0] = 0
        print(sample[0])
        assert None is sample.__mapper__
