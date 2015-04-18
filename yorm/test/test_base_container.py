#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201,W0212,C0111

"""Unit tests for the `base.container` module."""

import pytest

from yorm.base.container import Container


class TestContainer:

    """Unit tests for the `Container` class."""

    def test_not_implemented(self):
        """Verify `Container` cannot be used directly."""
        with pytest.raises(TypeError):
            Container()  # pylint: disable=E0110
        with pytest.raises(NotImplementedError):
            Container.default()
        with pytest.raises(NotImplementedError):
            Container.apply(None, None)


if __name__ == '__main__':
    pytest.main()
