#!/usr/bin/env python
# pylint:disable=R0201

"""Unit tests for the `utilities` module."""

import pytest
from unittest.mock import patch, Mock

from yorm import utilities


class TestStore:

    """Unit tests for the `store` function."""

    class Sample:

        """Sample class."""

    def test_no_attrs(self):
        """Verify mapping can be enabled with no attributes."""
        sample = utilities.store(self.Sample(), "sample.yml", None)
        assert sample.__path__ == "sample.yml"


class TestStoreInstances:

    """Unit tests for the `store_instances` decorator."""

    @utilities.store_instances("sample.yml")
    class SampleDecorated:

        """Sample decorated class using a single path."""

    @utilities.store_instances("{UUID}.yml")
    class SampleDecoratedUUID:

        """Sample decorated class using UUIDs for paths."""

    def test_no_attrs(self):
        """Verify mapping can be enabled with no attributes."""
        sample = self.SampleDecorated()
        assert sample.__path__ == "sample.yml"

    @patch('uuid.uuid4', Mock(return_value=Mock(hex='abc123')))
    def test_uuid(self):
        """Verify UUIDs can be used for filename."""
        sample = self.SampleDecoratedUUID()
        assert sample.__path__ == "abc123.yml"


if __name__ == '__main__':
    pytest.main()
