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

    @staticmethod
    def pm_to_dm(model):
        config = Config(model.key)
        config.name = model.name
        config.root = model.root
        return config


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
