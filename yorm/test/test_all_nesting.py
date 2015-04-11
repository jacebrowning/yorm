#!/usr/bin/env python
# pylint:disable=R0201,C0111

"""Integration tests for nested attributes."""

from unittest.mock import patch

import pytest

import yorm

from . import strip


@yorm.attr(all=yorm.converters.Integer)
class NestedList2(yorm.converters.List):

    def __repr__(self):
        return "<nested-list-2 {}>".format((id(self)))


@yorm.attr(number=yorm.converters.Integer)
class NestedDictionary2(yorm.converters.AttributeDictionary):

    def __init__(self):
        super().__init__()
        self.number = 0

    def __repr__(self):
        return "<nested-dictionary-2 {}>".format((id(self)))


@yorm.attr(number=yorm.converters.Integer)
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
class TestNesting:

    def test_list_append_triggers_update(self):
        top = Top()
        top.nested_list.append({'number': 1})
        assert strip("""
        nested_dict:
          number: 0
          numbers: []
        nested_list:
        - number: 1
        """) == top.yorm_mapper.text

    def test_list_append_triggers_update2(self):
        top = Top()
        top.nested_list.append({'number': 1})
        assert strip("""
        nested_dict:
          number: 0
          numbers: []
        nested_list:
        - number: 1
        """) == top.yorm_mapper.text

    def test_dict_set_triggers_update(self):
        top = Top()
        top.nested_dict.number = 2
        assert strip("""
        nested_dict:
          number: 2
          numbers: []
        nested_list: []
        """) == top.yorm_mapper.text

    def test_list_item_value_change_triggers_update(self):
        top = Top()
        top.nested_list = [{'number': 3}]
        assert strip("""
        nested_dict:
          number: 0
          numbers: []
        nested_list:
        - number: 3
        """) == top.yorm_mapper.text
        top.nested_list[0].number = 4
        assert strip("""
        nested_dict:
          number: 0
          numbers: []
        nested_list:
        - number: 4
        """) == top.yorm_mapper.text

    def test_dict_item_value_change_triggers_update(self):
        top = Top()
        top.nested_dict = {'numbers': [5]}
        assert strip("""
        nested_dict:
          number: 0
          numbers:
          - 5
        nested_list: []
        """) == top.yorm_mapper.text
        top.nested_dict.numbers.append(6)
        assert strip("""
        nested_dict:
          number: 0
          numbers:
          - 5
          - 6
        nested_list: []
        """) == top.yorm_mapper.text


if __name__ == '__main__':
    pytest.main()
