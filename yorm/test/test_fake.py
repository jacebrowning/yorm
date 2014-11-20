#!/usr/bin/env python
# pylint:disable=R0201

"""Integration tests for the `yorm.fake` option."""

import pytest
from unittest.mock import patch

import yorm  # pylint: disable=W0611


@patch('yorm.fake', True)
class TestFakeEnabled:

    """Integration tests with `yorm.fake` enabled."""

    # TODO: add a sample class here

    # TODO: add tests here


if __name__ == '__main__':
    pytest.main()
