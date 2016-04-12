"""Custom exceptions."""

from abc import ABCMeta

import yaml


class Error(Exception, metaclass=ABCMeta):
    """Base class for all YORM exceptions."""


class DuplicateMappingError(Error, FileExistsError):
    """A file path is already in use by another mapping."""


class DeletedFileError(Error, FileNotFoundError):
    """Text could not be read from a deleted file."""


class FileContentError(Error, yaml.error.YAMLError, ValueError):
    """Text could not be parsed as valid YAML."""
