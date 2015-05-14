#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201,W0212,C0111

"""Unit tests for the `base.converter` module."""

import pytest

from yorm.base.converter import Converter


class TestConverter:

    """Unit tests for the `Converter` class."""

    def test_converter_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Converter()  # pylint: disable=E0110


if __name__ == '__main__':
    pytest.main()
