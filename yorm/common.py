"""Shared internal classes and functions."""

import os
import shutil
import collections
import logging

import simplejson as json
import yaml

from . import exceptions


# CONSTANTS ####################################################################


PRINT_VERBOSITY = 0  # minimum verbosity to using `print`
STR_VERBOSITY = 3  # minimum verbosity to use verbose `__str__`
MAX_VERBOSITY = 4  # maximum verbosity level implemented

OVERRIDE_MESSAGE = "Method must be implemented in subclasses"


# GLOBALS ######################################################################


verbosity = 0  # global verbosity setting for controlling string formatting

attrs = collections.defaultdict(dict)


# LOGGING ######################################################################


def _trace(self, message, *args, **kwargs):  # pragma: no cover (manual test)
    """Handler for a new TRACE logging level."""
    if self.isEnabledFor(logging.DEBUG - 1):
        self._log(logging.DEBUG - 1, message, args, **kwargs)  # pylint: disable=protected-access


logging.addLevelName(logging.DEBUG - 1, "TRACE")
logging.Logger.trace = _trace

logger = logging.getLogger
log = logger(__name__)


# DECORATORS ###################################################################


class classproperty(object):
    """Read-only class property decorator."""

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


# FUNCTIONS ####################################################################


def create_dirname(path):
    """Ensure a parent directory exists for a path."""
    dirpath = os.path.dirname(path)
    if dirpath and not os.path.isdir(dirpath):
        log.trace("Creating directory '{}'...".format(dirpath))
        os.makedirs(dirpath)


def read_text(path, encoding='utf-8'):
    """Read text from a file.

    :param path: file path to read from
    :param encoding: input file encoding

    :return: string

    """
    log.trace("Reading text from '{}'...".format(path))
    with open(path, 'r', encoding=encoding) as stream:
        text = stream.read()
    return text


def load_file(text, path, ext='yml'):
    """Parse a dictionary from YAML text.

    :param text: string containing dumped YAML data
    :param path: file path for error messages

    :return: dictionary

    """
    data = {}

    try:
        if ext in ['yml', 'yaml']:
            data = yaml.load(text) or {}
        elif ext in ['json']:
            data = json.loads(text) or {}
    except yaml.error.YAMLError as exc:
        msg = "Invalid YAML contents: {}:\n{}".format(path, exc)
        raise exceptions.ContentError(msg) from None
    except json.JSONDecodeError as exc:
        msg = "Invalid JSON contents: {}:\n{}".format(path, exc)
        raise exceptions.ContentError(msg) from None

    # Ensure data is a dictionary
    if not isinstance(data, dict):
        msg = "Invalid file contents: {}".format(path)
        raise exceptions.ContentError(msg)

    return data


def dump_file(data, ext):
    if ext in ['json']:
        return json.dumps(data, indent=4, sort_keys=True)

    if ext not in ['yml', 'yaml']:
        log.warning("Unrecognized file extension: %s", ext)

    return yaml.dump(data, default_flow_style=False, allow_unicode=True)


def write_text(text, path, encoding='utf-8'):
    """Write text to a file.

    :param text: string
    :param path: file to write text
    :param encoding: output file encoding

    :return: path of new file

    """
    if text:
        log.trace("Writing text to '{}'...".format(path))

    with open(path, 'wb') as stream:
        data = text.encode(encoding)
        stream.write(data)

    return path


def touch(path):
    """Ensure a file exists."""
    if not os.path.exists(path):
        dirpath = os.path.dirname(path)
        if dirpath and not os.path.isdir(dirpath):
            log.trace("Creating directory '{}'...".format(dirpath))
            os.makedirs(dirpath)
        log.trace("Creating empty '{}'...".format(path))
        write_text('', path)


def stamp(path):
    """Get the modification timestamp from a file."""
    return os.path.getmtime(path)


def delete(path):
    """Delete a file or directory with error handling."""
    if os.path.isdir(path):
        try:
            log.trace("Deleting '{}'...".format(path))
            shutil.rmtree(path)
        except IOError:
            # bug: http://code.activestate.com/lists/python-list/159050
            msg = "Unable to delete: {}".format(path)
            log.warning(msg)
    elif os.path.isfile(path):
        log.trace("Deleting '{}'...".format(path))
        os.remove(path)
