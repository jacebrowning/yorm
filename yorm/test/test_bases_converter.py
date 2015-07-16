#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201,W0212,C0111

"""Unit tests for the `base.converter` module."""

import pytest

from yorm.bases import Converter


class TestConverter:

    """Unit tests for the `Converter` class."""

    def test_converter_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Converter()  # pylint: disable=E0110

    def test_converter_class_methods_cannot_be_called(self):
        with pytest.raises(NotImplementedError):
            Converter.create_default()
        with pytest.raises(NotImplementedError):
            Converter.to_value(None)
        with pytest.raises(NotImplementedError):
            Converter.to_data(None)


if __name__ == '__main__':
    pytest.main()
