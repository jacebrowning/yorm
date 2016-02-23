# pylint: disable=missing-docstring,no-self-use,abstract-class-instantiated

import pytest

from yorm.bases import Converter


class TestConverter:

    """Unit tests for the `Converter` class."""

    def test_converter_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Converter()

    def test_converter_class_methods_cannot_be_called(self):
        with pytest.raises(NotImplementedError):
            Converter.create_default()
        with pytest.raises(NotImplementedError):
            Converter.to_value(None)
        with pytest.raises(NotImplementedError):
            Converter.to_data(None)
