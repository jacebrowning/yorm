#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201,W0212,C0111

"""Unit tests for the `base.convertible` module."""

import pytest

from yorm.base.convertible import Convertible


class TestConvertible:

    """Unit tests for the `Convertible` class."""

    def test_convertible_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Convertible()  # pylint: disable=E0110

    def test_convertible_class_methods_cannot_be_called(self):
        with pytest.raises(NotImplementedError):
            Convertible.create_default()
        with pytest.raises(NotImplementedError):
            Convertible.update_value(None, None)


if __name__ == '__main__':
    pytest.main()
