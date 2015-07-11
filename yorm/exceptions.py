"""Custom exceptions."""

import yaml


class YORMException(Exception):

    """Base class for all YORM exceptions."""


class FileError(YORMException, FileNotFoundError):

    """Raised when text cannot be read from a file."""


class ContentError(YORMException, yaml.error.YAMLError, ValueError):

    """Raised when YAML cannot be parsed from text."""


class ConversionError(YORMException, ValueError):

    """Raised when a value cannot be converted to the specified type."""


class UseageError(YORMException):

    """Raised when an API is called incorrectly."""
