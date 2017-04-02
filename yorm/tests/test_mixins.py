# pylint: disable=unused-variable,expression-not-assigned

from unittest.mock import patch, call

import pytest
from expecter import expect

import yorm
from yorm.mixins import ModelMixin


def describe_model_mixin():

    @pytest.fixture
    def mixed_class():

        @yorm.sync("tmp/model.yml")
        class MyClass(ModelMixin):
            pass

        return MyClass

    @pytest.fixture
    def mixed_instance(mixed_class):
        return mixed_class()

    @patch('yorm.mixins.utilities')
    def it_adds_a_create_method(utilities, mixed_class):
        mixed_class.create('foobar', overwrite=True)

        expect(utilities.mock_calls) == [
            call.create(mixed_class, 'foobar', overwrite=True)
        ]

    @patch('yorm.mixins.utilities')
    def it_adds_a_find_method(utilities, mixed_class):
        mixed_class.find('foobar', create=True)

        expect(utilities.mock_calls) == [
            call.find(mixed_class, 'foobar', create=True)
        ]

    @patch('yorm.mixins.utilities')
    def it_adds_a_match_method(utilities, mixed_class):
        mixed_class.match(foo='bar')

        expect(utilities.mock_calls) == [
            call.match(mixed_class, foo='bar')
        ]

    @patch('yorm.mixins.utilities')
    def it_adds_a_load_method(utilities, mixed_instance):
        mixed_instance.load()

        expect(utilities.mock_calls) == [
            call.load(mixed_instance)
        ]

    @patch('yorm.mixins.utilities')
    def it_adds_a_save_method(utilities, mixed_instance):
        mixed_instance.save()

        expect(utilities.mock_calls) == [
            call.save(mixed_instance)
        ]

    @patch('yorm.mixins.utilities')
    def it_adds_a_delete_method(utilities, mixed_instance):
        mixed_instance.delete()

        expect(utilities.mock_calls) == [
            call.delete(mixed_instance)
        ]
