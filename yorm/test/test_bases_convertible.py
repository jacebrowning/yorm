#!/usr/bin/env python
# pylint:disable=W0201,W0613,R,C

"""Unit tests for the `base.convertible` module."""

import pytest

from yorm.bases import Convertible


class TestConvertible:

    """Unit tests for the `Convertible` class."""

    class MyConvertible(Convertible):

        def __init__(self, number):
            from unittest.mock import MagicMock
            self.yorm_mapper = MagicMock()
            self.value = number

        @classmethod
        def create_default(cls):
            return 1

        @classmethod
        def to_data(cls, value):
            return str(value.value)

        def update_value(self, data, match=None):
            self.value += int(data)

    def test_convertible_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Convertible()  # pylint: disable=E0110

    def test_convertible_instance_methods_can_be_called(self):
        convertible = self.MyConvertible(42)
        assert 42 == convertible.value
        convertible.update_value(10)
        assert 52 == convertible.value
        assert "52" == convertible.format_data()


if __name__ == '__main__':
    pytest.main()
