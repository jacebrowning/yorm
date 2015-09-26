#!/usr/bin/env python
# pylint:disable=R,C

"""Integration tests using YORM as a persistence model."""

import os

import yorm


class Config:

    def __init__(self, key, name=None, root=None):
        self.key = key
        self.name = name or ""
        self.root = root or ""


@yorm.attr(key=yorm.converters.String)
@yorm.attr(name=yorm.converters.String)
@yorm.sync("{self.root}/{self.key}/config.yml")
class ConfigModel:

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
        self.path = self.root + "/{}/config.yml"
        self.attrs = dict(key=yorm.converters.String,
                          name=yorm.converters.String)

    def read(self, key):
        instance = Config(key)
        path = self.path.format(key)
        attrs = self.attrs
        try:
            yorm.sync(instance, path, attrs, existing=True, auto=False)
        except yorm.exceptions.FileMissingError:
            return None
        else:
            yorm.update_object(instance)
            return instance


class TestPersistanceMapping:

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
        yorm.update(model, force=True)
        assert 42 == model.unmapped


class TestStore:

    def test_read_missing(self, tmpdir):
        store = ConfigStore(str(tmpdir))
        assert None is store.read('unknown')
