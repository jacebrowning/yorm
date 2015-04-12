#!/usr/bin/env python
# pylint:disable=R0201,C0111

"""Integration tests for nested attributes."""

from unittest.mock import patch

import pytest

import yorm

from . import strip


@yorm.attr(all=yorm.converters.Float)
class NestedList2(yorm.converters.List):

    def __repr__(self):
        return "<nested-list-2 {}>".format((id(self)))


@yorm.attr(number=yorm.converters.Float)
class NestedDictionary2(yorm.converters.AttributeDictionary):

    def __init__(self):
        super().__init__()
        self.number = 0

    def __repr__(self):
        return "<nested-dictionary-2 {}>".format((id(self)))


@yorm.attr(number=yorm.converters.Float)
@yorm.attr(numbers=NestedList2)
class NestedDictionary(yorm.converters.AttributeDictionary):

    def __init__(self):
        super().__init__()
        self.number = 0
        self.numbers = []

    def __repr__(self):
        return "<nested-dictionary {}>".format((id(self)))


@yorm.attr(all=NestedDictionary2)
class NestedList(yorm.converters.List):

    def __repr__(self):
        return "<nested-list {}>".format((id(self)))


@yorm.attr(nested_list=NestedList, nested_dict=NestedDictionary)
@yorm.sync("sample.yml")
class Top:

    def __init__(self):
        self.nested_list = []
        self.nested_dict = {}

    def __repr__(self):
        return "<top {}>".format((id(self)))


@patch('yorm.settings.fake', True)
class TestTop:

    def test_append_triggers_store(self):
        top = Top()
        top.nested_list.append({'number': 1})
        assert strip("""
        nested_dict:
          number: 0.0
          numbers: []
        nested_list:
        - number: 1.0
        """) == top.yorm_mapper.text

    def test_set_by_index_triggers_store(self):
        top = Top()
        top.nested_list = [{'number': 1.5}]
        assert strip("""
        nested_dict:
          number: 0.0
          numbers: []
        nested_list:
        - number: 1.5
        """) == top.yorm_mapper.text
        top.nested_list[0] = {'number': 1.6}
        assert strip("""
        nested_dict:
          number: 0.0
          numbers: []
        nested_list:
        - number: 1.6
        """) == top.yorm_mapper.text

    def test_get_by_index_triggers_fetch(self):
        top = Top()
        top.yorm_mapper.text = strip("""
        nested_list:
        - number: 1.7
        """)
        assert 1.7 == top.nested_list[0].number

    def test_delete_index_triggers_store(self):
        top = Top()
        top.nested_list = [{'number': 1.8}, {'number': 1.9}]
        assert strip("""
        nested_dict:
          number: 0.0
          numbers: []
        nested_list:
        - number: 1.8
        - number: 1.9
        """) == top.yorm_mapper.text
        del top.nested_list[0]
        assert strip("""
        nested_dict:
          number: 0.0
          numbers: []
        nested_list:
        - number: 1.9
        """) == top.yorm_mapper.text

    def test_set_dict_as_attribute_triggers_store(self):
        top = Top()
        top.nested_dict.number = 2
        assert strip("""
        nested_dict:
          number: 2.0
          numbers: []
        nested_list: []
        """) == top.yorm_mapper.text


@patch('yorm.settings.fake', True)
class TestNested:

    def test_list_item_value_change_triggers_store(self):
        top = Top()
        top.nested_list = [{'number': 3}]
        assert strip("""
        nested_dict:
          number: 0.0
          numbers: []
        nested_list:
        - number: 3.0
        """) == top.yorm_mapper.text
        top.nested_list[0].number = 4
        assert strip("""
        nested_dict:
          number: 0.0
          numbers: []
        nested_list:
        - number: 4.0
        """) == top.yorm_mapper.text

    def test_dict_item_value_change_triggers_store(self):
        top = Top()
        top.nested_dict = {'numbers': [5]}
        assert strip("""
        nested_dict:
          number: 0.0
          numbers:
          - 5.0
        nested_list: []
        """) == top.yorm_mapper.text
        top.nested_dict.numbers.append(6)
        assert strip("""
        nested_dict:
          number: 0.0
          numbers:
          - 5.0
          - 6.0
        nested_list: []
        """) == top.yorm_mapper.text


if __name__ == '__main__':
    pytest.main()
