"""Functions to work with files and data formats."""

import os
import shutil

import simplejson as json
import yaml

from . import common, exceptions

log = common.logger(__name__)


def touch(path):
    """Ensure a file path exists."""
    if not os.path.exists(path):
        dirpath = os.path.dirname(path)
        if dirpath and not os.path.isdir(dirpath):
            log.trace("Creating directory '{}'...".format(dirpath))
            os.makedirs(dirpath)
        log.trace("Creating empty '{}'...".format(path))
        write("", path)


def read(path, encoding='utf-8'):
    """Read text from a file.

    :param path: file path to read from
    :param encoding: input file encoding

    :return: string contents of file

    """
    log.trace("Reading text from '{}'...".format(path))

    with open(path, 'r', encoding=encoding) as stream:
        text = stream.read()

    return text


def write(text, path, encoding='utf-8'):
    """Write text to a file.

    :param text: string
    :param path: file path to write text
    :param encoding: output file encoding

    :return: path of file

    """
    if text:
        log.trace("Writing text to '{}'...".format(path))

    with open(path, 'wb') as stream:
        data = text.encode(encoding)
        stream.write(data)

    return path


def stamp(path):
    """Get the modification timestamp from a file."""
    return os.path.getmtime(path)


def delete(path):
    """Delete a file or directory."""
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


def load(text, path, ext='yml'):
    """Parse a dictionary a data from formatted text.

    :param text: string containing dumped data
    :param path: file path for error messages

    :return: dictionary of data

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


def dump(data, ext):
    """Format a dictionary into a serialization format."""
    if ext in ['json']:
        return json.dumps(data, indent=4, sort_keys=True)

    if ext not in ['yml', 'yaml']:
        log.warning("Unrecognized file extension: %s", ext)

    return yaml.dump(data, default_flow_style=False, allow_unicode=True)
