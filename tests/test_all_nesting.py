#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201,C0111

"""Integration tests for nested attributes."""

from unittest.mock import patch
import logging

import pytest

import yorm

from . import strip


@yorm.attr(status=yorm.converters.Boolean)
class StatusDictionary(yorm.converters.Dictionary):

    pass


@yorm.attr(all=yorm.converters.Float)
class NestedList3(yorm.converters.List):

    def __repr__(self):
        return "<nested-list-3 {}>".format((id(self)))


@yorm.attr(number=yorm.converters.Float)
@yorm.attr(nested_list_3=NestedList3)
class NestedDictionary3(yorm.converters.AttributeDictionary):

    def __init__(self):
        super().__init__()
        self.number = 0
        self.nested_list_3 = []

    def __repr__(self):
        print(self.number)  # trigger a potential recursion issue
        return "<nested-dictionary-3 {}>".format((id(self)))


@yorm.attr(all=yorm.converters.Float)
class NestedList2(yorm.converters.List):

    def __repr__(self):
        return "<nested-list-2 {}>".format((id(self)))


@yorm.attr(nested_dict_3=NestedDictionary3)
@yorm.attr(number=yorm.converters.Float)
class NestedDictionary2(yorm.converters.AttributeDictionary):

    def __init__(self):
        super().__init__()
        self.number = 0

    def __repr__(self):
        print(self.number)  # trigger a potential recursion issue
        return "<nested-dictionary-2 {}>".format((id(self)))


@yorm.attr(number=yorm.converters.Float)
@yorm.attr(nested_list_2=NestedList2)
class NestedDictionary(yorm.converters.AttributeDictionary):

    def __init__(self):
        super().__init__()
        self.number = 0
        self.nested_list_2 = []

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
class TestNestedOnce:

    def test_append_triggers_store(self):
        top = Top()
        logging.info("appending dictionary to list...")
        top.nested_list.append({'number': 1})
        assert strip("""
        nested_dict:
          nested_list_2: []
          number: 0.0
        nested_list:
        - nested_dict_3:
            nested_list_3: []
            number: 0.0
          number: 1.0
        """) == top.yorm_mapper.text

    def test_set_by_index_triggers_store(self):
        top = Top()
        top.nested_list = [{'number': 1.5}]
        assert strip("""
        nested_dict:
          nested_list_2: []
          number: 0.0
        nested_list:
        - nested_dict_3:
            nested_list_3: []
            number: 0.0
          number: 1.5
        """) == top.yorm_mapper.text
        top.nested_list[0] = {'number': 1.6}
        assert strip("""
        nested_dict:
          nested_list_2: []
          number: 0.0
        nested_list:
        - nested_dict_3:
            nested_list_3: []
            number: 0.0
          number: 1.6
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
          nested_list_2: []
          number: 0.0
        nested_list:
        - nested_dict_3:
            nested_list_3: []
            number: 0.0
          number: 1.8
        - nested_dict_3:
            nested_list_3: []
            number: 0.0
          number: 1.9
        """) == top.yorm_mapper.text
        del top.nested_list[0]
        assert strip("""
        nested_dict:
          nested_list_2: []
          number: 0.0
        nested_list:
        - nested_dict_3:
            nested_list_3: []
            number: 0.0
          number: 1.9
        """) == top.yorm_mapper.text

    def test_set_dict_as_attribute_triggers_store(self):
        top = Top()
        top.nested_dict.number = 2
        assert strip("""
        nested_dict:
          nested_list_2: []
          number: 2.0
        nested_list: []
        """) == top.yorm_mapper.text


@patch('yorm.settings.fake', True)
class TestNestedTwice:

    def test_nested_list_item_value_change_triggers_store(self):
        top = Top()
        top.nested_list = [{'number': 3}]
        assert strip("""
        nested_dict:
          nested_list_2: []
          number: 0.0
        nested_list:
        - nested_dict_3:
            nested_list_3: []
            number: 0.0
          number: 3.0
        """) == top.yorm_mapper.text
        top.nested_list[0].number = 4
        assert strip("""
        nested_dict:
          nested_list_2: []
          number: 0.0
        nested_list:
        - nested_dict_3:
            nested_list_3: []
            number: 0.0
          number: 4.0
        """) == top.yorm_mapper.text

    def test_nested_dict_item_value_change_triggers_store(self):
        top = Top()
        top.nested_dict = {'nested_list_2': [5]}
        assert strip("""
        nested_dict:
          nested_list_2:
          - 5.0
          number: 0.0
        nested_list: []
        """) == top.yorm_mapper.text
        top.nested_dict.nested_list_2.append(6)
        assert strip("""
        nested_dict:
          nested_list_2:
          - 5.0
          - 6.0
          number: 0.0
        nested_list: []
        """) == top.yorm_mapper.text

    def test_dict_in_list_value_change_triggers_store(self):
        top = Top()
        top.nested_list.append(None)
        top.nested_list[0].nested_dict_3.number = 8
        assert strip("""
        nested_dict:
          nested_list_2: []
          number: 0.0
        nested_list:
        - nested_dict_3:
            nested_list_3: []
            number: 8.0
          number: 0.0
        """) == top.yorm_mapper.text

    def test_list_in_dict_append_triggers_store(self):
        top = Top()
        top.nested_list.append(None)
        top.nested_list.append(None)
        for nested_dict_2 in top.nested_list:
            nested_dict_2.number = 9
            nested_dict_2.nested_dict_3.nested_list_3.append(10)
        assert strip("""
        nested_dict:
          nested_list_2: []
          number: 0.0
        nested_list:
        - nested_dict_3:
            nested_list_3:
            - 10.0
            number: 0.0
          number: 9.0
        - nested_dict_3:
            nested_list_3:
            - 10.0
            number: 0.0
          number: 9.0
        """) == top.yorm_mapper.text


@patch('yorm.settings.fake', True)
class TestAliases:

    @yorm.attr(var4=NestedList3)
    @yorm.attr(var5=StatusDictionary)
    @yorm.sync("fake/path")
    class Sample:

        def __repr__(self):
            return "<sample {}>".format(id(self))

    def setup_method(self, method):
        self.sample = self.Sample()

    @staticmethod
    def _log_ref(name, var, ref):
        logging.info("%s: %r", name, var)
        logging.info("%s_ref: %r", name, ref)
        logging.info("%s ID: %s", name, id(var))
        logging.info("%s_ref ID: %s", name, id(ref))
        assert id(ref) == id(var)
        assert ref == var

    def test_alias_list(self):
        yorm.update_object(self.sample)
        var4_ref = self.sample.var4
        self._log_ref('var4', self.sample.var4, var4_ref)
        assert [] == self.sample.var4

        logging.info("appending 42 to var4_ref...")
        var4_ref.append(42)
        self._log_ref('var4', self.sample.var4, var4_ref)
        assert [42] == self.sample.var4

        logging.info("appending 2015 to var4_ref...")
        var4_ref.append(2015)
        assert [42, 2015] == self.sample.var4

    def test_alias_dict(self):
        yorm.update_object(self.sample)
        var5_ref = self.sample.var5
        self._log_ref('var5', self.sample.var5, var5_ref)
        assert {'status': False} == self.sample.var5

        logging.info("setting status=True in var5_ref...")
        var5_ref['status'] = True
        self._log_ref('var5', self.sample.var5, var5_ref)
        assert {'status': True} == self.sample.var5

        logging.info("setting status=False in var5_ref...")
        var5_ref['status'] = False
        self._log_ref('var5', self.sample.var5, var5_ref)
        assert {'status': False} == self.sample.var5

    def test_alias_dict_in_list(self):
        top = Top()
        top.nested_list.append(None)
        ref1 = top.nested_list[0]
        ref2 = top.nested_list[0].nested_dict_3
        ref3 = top.nested_list[0].nested_dict_3.nested_list_3
        yorm.update(top)
        assert id(ref1) == id(top.nested_list[0])
        assert id(ref2) == id(top.nested_list[0].nested_dict_3)
        assert id(ref3) == id(top.nested_list[0].nested_dict_3.nested_list_3)

    def test_alias_list_in_dict(self):
        top = Top()
        logging.info("updating nested attribute...")
        top.nested_dict.number = 1
        logging.info("storing refs...")
        ref1 = top.nested_dict
        ref2 = top.nested_dict.nested_list_2
        yorm.update(top)
        assert id(ref1) == id(top.nested_dict)
        assert id(ref2) == id(top.nested_dict.nested_list_2)


if __name__ == '__main__':
    pytest.main()
