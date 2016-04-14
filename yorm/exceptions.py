"""Custom exceptions."""

from abc import ABCMeta

import yaml


class Error(Exception, metaclass=ABCMeta):
    """Base class for all YORM exceptions."""


class DuplicateMappingError(Error, FileExistsError):
    """The file is already in use by another mapping."""


class MissingFileError(Error, FileNotFoundError):
    """An object's file has not yet been created."""


class DeletedFileError(Error, FileNotFoundError):
    """An object's file was deleted."""


class FileContentError(Error, yaml.error.YAMLError, ValueError):
    """Text could not be parsed as valid YAML."""
