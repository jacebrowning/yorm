"""Custom exceptions."""

from abc import ABCMeta

import yaml


class Error(Exception, metaclass=ABCMeta):

    """Base class for all YORM exceptions."""


class FileMissingError(Error, FileNotFoundError):

    """A file was expected to exist."""


class FileAlreadyExistsError(Error, FileExistsError):

    """A file was not expected to exist."""


class FileDeletedError(Error, FileNotFoundError):

    """Text could not be read from a deleted file."""


class ContentError(Error, yaml.error.YAMLError, ValueError):

    """Text could not be parsed as valid YAML."""


class ConversionError(Error, ValueError):

    """Value could not be converted to the specified type."""


class MappingError(Error):

    """The API was called incorrectly."""
