#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201,W0212,C0111

"""Unit tests for the `base.convertible` module."""

import pytest

from yorm.base.convertible import Convertible


class TestConvertible:

    """Unit tests for the `Convertible` class."""

    def test_not_implemented(self):
        """Verify `Convertible` cannot be used directly."""
        with pytest.raises(NotImplementedError):
            Convertible()  # pylint: disable=E0110


if __name__ == '__main__':
    pytest.main()
