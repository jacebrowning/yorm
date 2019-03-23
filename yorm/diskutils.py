"""Functions to work with files and data formats."""

import os
import shutil
import logging

import yaml
import simplejson as json

from . import exceptions

log = logging.getLogger(__name__)


def exists(path):
    """Determine if a path exists."""
    return os.path.exists(path)


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


def parse(text, path):
    """Parse a dictionary of data from formatted text.

    :param text: string containing dumped data
    :param path: file path to specify formatting

    :return: dictionary of data

    """
    ext = _get_ext(path)
    if ext in ['json']:
        data = _parse_json(text, path)
    elif ext in ['yml', 'yaml']:
        data = _parse_yaml(text, path)
    else:
        log.warning("Unrecognized file extension (.%s), assuming YAML", ext)
        data = _parse_yaml(text, path)

    if not isinstance(data, dict):
        msg = "Invalid file contents: {}".format(path)
        raise exceptions.FileContentError(msg)

    return data


def _parse_json(text, path):
    try:
        return json.loads(text) or {}
    except json.JSONDecodeError:
        msg = "Invalid JSON contents: {}:\n{}".format(path, text)
        raise exceptions.FileContentError(msg)


def _parse_yaml(text, path):
    try:
        return yaml.safe_load(text) or {}
    except yaml.error.YAMLError:
        msg = "Invalid YAML contents: {}:\n{}".format(path, text)
        raise exceptions.FileContentError(msg)


def dump(data, path):
    """Format a dictionary into a serialization format.

    :param text: dictionary of data to format
    :param path: file path to specify formatting

    :return: string of formatted data

    """
    ext = _get_ext(path)

    if ext in ['json']:
        return json.dumps(data, indent=4, sort_keys=True)

    if ext not in ['yml', 'yaml']:
        log.warning("Unrecognized file extension (.%s), assuming YAML", ext)

    return yaml.dump(data, default_flow_style=False, allow_unicode=True)


def _get_ext(path):
    if '.' in path:
        return path.split('.')[-1].lower()
    else:
        return 'yml'
