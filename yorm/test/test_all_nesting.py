#!/usr/bin/env python
# pylint:disable=R0201,C0111

"""Integration tests for nested attributes."""

from unittest.mock import patch

import pytest
import yorm

from . import strip


@yorm.attr(status=yorm.standard.Boolean)
class NestedDict(yorm.container.Dictionary):
    pass


@yorm.attr(all=NestedDict)
class NestedList(yorm.container.List):
    pass


@yorm.attr(nested_list=NestedList, nested_dict=NestedDict)
@yorm.sync("sample.yml")
class Top:

    def __init__(self):
        self.nested_list = []
        self.nested_dict = {}


@patch('yorm.settings.fake', True)
class TestNesting:

    def test_list_append_triggers_update(self):
        top = Top()
        top.nested_list.append(None)
        assert strip("""
        nested_dict:
          status: false
        nested_list:
        - status: false
        """) == top.yorm_mapper.fake

    def test_dict_set_triggers_update(self):
        top = Top()
        top.nested_dict['status'] = 1
        assert strip("""
        nested_dict:
          status: true
        nested_list: []
        """) == top.yorm_mapper.fake

    def test_dict_in_list_triggers_update(self):
        top = Top()
        top.nested_list = {'status': True}
        assert strip("""
        nested_dict:
          status: false
        nested_list:
        - status: true
        """) == top.yorm_mapper.fake
        top.nested_list[0]['status'] = False
        assert strip("""
        nested_dict:
          status: false
        nested_list:
        - status: false
        """) == top.yorm_mapper.fake


if __name__ == '__main__':
    pytest.main()
