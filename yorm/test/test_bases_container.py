# pylint: disable=missing-docstring,no-self-use,misplaced-comparison-constant,abstract-class-instantiated

import pytest

from yorm.bases import Container


class TestContainer:
    """Unit tests for the `Container` class."""

    class MyContainer(Container):

        def __init__(self, number):
            from unittest.mock import MagicMock
            self.__mapper__ = MagicMock()
            self.value = number

        @classmethod
        def create_default(cls):
            return 1

        @classmethod
        def to_data(cls, value):
            return str(value.value)

        def update_value(self, data, *, auto_track=None):  # pylint: disable=unused-variable
            self.value += int(data)

    def test_container_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Container()

    def test_container_instance_methods_can_be_called(self):
        container = self.MyContainer(42)
        assert 42 == container.value
        container.update_value(10)
        assert 52 == container.value
        assert "52" == container.format_data()
