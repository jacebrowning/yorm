"""Integration tests using YORM as a persistence model."""
# pylint: disable=missing-docstring,no-self-use,misplaced-comparison-constant

import os

from expecter import expect

import yorm
from yorm.types import String


# CLASSES ######################################################################


class Config:
    """Domain model."""

    def __init__(self, key, name=None, root=None):
        self.key = key
        self.name = name or ""
        self.root = root or ""


@yorm.attr(key=String)
@yorm.attr(name=String)
@yorm.sync("{self.root}/{self.key}/config.yml",
           auto_create=False, auto_save=False)
class ConfigModel:
    """Persistence model."""

    def __init__(self, key, root):
        self.key = key
        self.root = root
        print(self.key)
        self.unmapped = 0

    @staticmethod
    def pm_to_dm(model):
        config = Config(model.key)
        config.name = model.name
        config.root = model.root
        return config


class ConfigStore:

    def __init__(self, root):
        self.root = root

    def read(self, key):
        return yorm.find(ConfigModel, self.root, key)


# TESTS ########################################################################


class TestPersistanceMapping:  # pylint: disable=no-member

    root = os.path.join(os.path.dirname(__file__), 'files')

    def test_load_pm(self):
        model = ConfigModel('my_key', self.root)

        print(model.__dict__)
        assert model.key == "my_key"
        assert model.root == self.root
        assert model.name == "my_name"

    def test_create_dm_from_pm(self):
        model = ConfigModel('my_key', self.root)
        config = ConfigModel.pm_to_dm(model)

        print(config.__dict__)
        assert config.key == "my_key"
        assert config.root == self.root
        assert config.name == "my_name"

    def test_nonmapped_attribute_is_kept(self):
        model = ConfigModel('my_key', self.root)
        model.unmapped = 42
        assert 42 == model.unmapped

    def test_missing_files_are_handled(self):
        model = ConfigModel('my_key_manual', self.root)

        with expect.raises(yorm.exceptions.MissingFileError):
            print(model.name)


class TestStore:

    def test_read_missing(self, tmpdir):
        store = ConfigStore(str(tmpdir))
        assert None is store.read('unknown')
