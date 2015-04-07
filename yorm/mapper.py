"""Core YAML mapping functionality."""

import os
import functools

import yaml

from . import common
from . import settings

log = common.logger(__name__)


def file_required(method):
    """Decorator for methods that require the file to exist."""
    @functools.wraps(method)
    def decorated_method(self, *args, **kwargs):
        """Decorated method."""
        if not self.exists:
            msg = "cannot access deleted: {}".format(self.path)
            raise common.FileError(msg)
        return method(self, *args, **kwargs)
    return decorated_method


def fake_required(method):
    """Decorator for methods that require 'settings.fake' to be set."""
    @functools.wraps(method)
    def decorated_method(self, *args, **kwargs):
        """Decorated method."""
        if not settings.fake:
            raise AttributeError("'fake' only available with 'settings.fake'")
        return method(self, *args, **kwargs)
    return decorated_method


def prefix(obj):
    """Prefix a string with a fake designator if enabled."""
    fake = "(fake) " if settings.fake else ""
    name = obj if isinstance(obj, str) else "'{}'".format(obj)
    return fake + name


class Mapper:

    """Utility class to manipulate YAML files.

    To start mapping attributes to a file:

        create -> [empty] -> FILE

    When getting an attribute:

        FILE -> read -> [text] -> load -> [dict] -> fetch -> ATTRIBUTES

    When setting an attribute:

        ATTRIBUTES -> store -> [dict] -> dump -> [text] -> write -> FILE

    After the mapped file is no longer needed:

        delete -> [null] -> FILE

    """

    def __init__(self, path):
        self.path = path
        self.auto = False
        self.exists = os.path.isfile(self.path)
        self._activity = False
        self._timestamp = 0
        self._fake = ""

    def __str__(self):
        return str(self.path)

    @property
    @fake_required
    def fake(self):
        """Get fake file contents (if enabled)."""
        return self._fake

    @fake.setter
    @fake_required
    def fake(self, text):
        """Set fake file contents (if enabled)."""
        self._fake = text
        self.modified = True

    def create(self, obj):
        """Create a new file for the object."""
        log.info("creating %s for %r...", prefix(self), obj)
        if self.exists:
            log.warning("already created: %s", self)
            return
        if not settings.fake:
            common.create_dirname(self.path)
            common.touch(self.path)
        self.modified = False
        self.exists = True

    @file_required
    def fetch(self, obj, attrs, force=False):
        """Update the object's mapped attributes from its file."""
        if self._activity:
            return
        if not self.modified and not force:
            return
        self._activity = True
        _force = "force-" if force else ""
        log.debug("%sfetching %r from %s...", _force, obj, prefix(self))

        # Parse data from file
        text = self._read()
        data = self._load(text, self.path)
        log.trace("loaded: {}".format(data))

        # Update attributes
        for name, data in data.items():
            try:
                converter = attrs[name]
            except KeyError:
                # TODO: determine if this runtime import is the best way to do this
                from . import standard
                converter = standard.match(name, data)
                attrs[name] = converter
            value = converter.to_value(data)
            log.trace("value fetched: '{}' = {}".format(name, repr(value)))
            setattr(obj, name, value)

        # Set meta attributes
        self.modified = False
        self._activity = False

    @file_required
    def _read(self):
        """Read text from the object's file.

        :param path: path to a text file

        :return: contexts of text file

        """
        if settings.fake:
            return self.fake
        else:
            return common.read_text(self.path)

    @staticmethod
    def _load(text, path):
        """Load YAML data from text.

        :param text: text read from a file
        :param path: path to the file (for displaying errors)

        :return: dictionary of YAML data

        """
        return common.load_yaml(text, path)

    @file_required
    def store(self, obj, attrs):
        """Format and save the object's mapped attributes to its file."""
        if self._activity:
            return
        self._activity = True
        log.debug("storing %r to %s...", obj, prefix(self))

        # Format the data items
        data = {}
        for name, converter in attrs.items():
            try:
                value = getattr(obj, name)
            except AttributeError as exc:
                log.debug(exc)
                value = None
            data2 = converter.to_data(value)
            log.trace("data to store: '%s' = %r", name, data2)
            data[name] = data2

        # Dump data to file
        text = self._dump(data)
        self._write(text)

        # Set meta attributes
        self.modified = False
        self._activity = False

    @staticmethod
    def _dump(data):
        """Dump YAML data to text.

        :param data: dictionary of YAML data

        :return: text to write to a file

        """
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)

    @file_required
    def _write(self, text):
        """Write text to the object's file.

        :param text: text to write to a file
        :param path: path to the file

        """
        if settings.fake:
            self.fake = text
        else:
            common.write_text(text, self.path)

    @property
    def modified(self):
        """Determine if the file has been modified."""
        if settings.fake:
            changes = self._timestamp is not None
            log.trace("file is %smodified (it is fake)",
                      "" if changes else "not ")
            return changes
        elif not self.exists:
            log.trace("file is modified (it is deleted)")
            return True
        else:
            was = self._timestamp
            now = common.stamp(self.path)
            log.trace("file is %smodified (%s -> %s)",
                      "not " if was == now else "",
                      was, now)
            return was != now

    @modified.setter
    def modified(self, changes):
        """Mark the file as modified if there are changes."""
        if changes:
            log.trace("marked %s as modified", prefix("file"))
            self._timestamp = 0
        else:
            if settings.fake:
                self._timestamp = None
            else:
                self._timestamp = common.stamp(self.path)
            log.trace("marked %s as not modified", prefix("file"))

    def delete(self):
        """Delete the object's file from the file system."""
        if self.exists:
            log.info("deleting %s...", prefix(self))
            if not settings.fake:
                common.delete(self.path)
            self.exists = False
        else:
            log.warning("already deleted: %s", self)
