"""Core YAML mapping functionality."""

import os
import functools

import yaml

from . import common
from . import settings

log = common.logger(__name__)


def readwrite(func):
    """Decorator for methods that require the file to exist."""
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        """Wrapped method."""
        if not self.exists:
            msg = "cannot access deleted: {}".format(self.path)
            raise common.FileError(msg)
        return func(self, *args, **kwargs)
    return wrapped


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
        self._retrieving = False
        self._storing = False
        self._timestamp = 0

    def __str__(self):
        return str(self.path)

    @property
    def _fake(self):  # pylint: disable=R0201
        """Get a string indicating the fake setting to use in logging."""
        return "(fake) " if settings.fake else ''

    def create(self, obj):
        """Create a new file for the object."""
        log.info("creating %s'%s' for %r...", self._fake, self, obj)
        if self.exists:
            log.warning("already created: %s", self)
            return
        if not self._fake:
            common.create_dirname(self.path)
            common.touch(self.path)
        self.modified = False
        self.exists = True

    @readwrite
    def fetch(self, obj, attrs, force=False):
        """Update the object's mapped attributes from its file."""
        if self._storing:
            return
        if not self.modified and not force:
            return
        self._retrieving = True
        log.debug("%sfetching %r from %s'%s'...", "force-" if force else "",
                  obj, self._fake, self.path)

        # Parse data from file
        if self._fake:
            text = getattr(obj, 'yorm_fake', "")
        else:
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
        self._retrieving = False

    @readwrite
    def _read(self):
        """Read text from the object's file.

        :param path: path to a text file

        :return: contexts of text file

        """
        return common.read_text(self.path)

    @staticmethod
    def _load(text, path):
        """Load YAML data from text.

        :param text: text read from a file
        :param path: path to the file (for displaying errors)

        :return: dictionary of YAML data

        """
        return common.load_yaml(text, path)

    @readwrite
    def store(self, obj, attrs):
        """Format and save the object's mapped attributes to its file."""
        if self._retrieving:
            return
        self._storing = True
        log.debug("storing %r to %s'%s'...", obj, self._fake, self.path)

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
        if self._fake:
            obj.yorm_fake = text
        else:
            self._write(text)

        # Set meta attributes
        self.modified = False
        self._storing = False

    @staticmethod
    def _dump(data):
        """Dump YAML data to text.

        :param data: dictionary of YAML data

        :return: text to write to a file

        """
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)

    @readwrite
    def _write(self, text):
        """Write text to the object's file.

        :param text: text to write to a file
        :param path: path to the file

        """
        common.write_text(text, self.path)

    @property
    def modified(self):
        """Determine if the file has been modified."""
        if self._fake:
            log.trace("file is modified (it is fake)")
            return True
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
            log.trace("marked %sfile as modified", self._fake)
            self._timestamp = 0
        else:
            if self._fake:
                self._timestamp = None
            else:
                self._timestamp = common.stamp(self.path)
            log.trace("marked %sfile as not modified", self._fake)

    def delete(self):
        """Delete the object's file from the file system."""
        if self.exists:
            log.info("deleting %s'%s'...", self._fake, self.path)
            if not self._fake:
                common.delete(self.path)
            self.exists = False
        else:
            log.warning("already deleted: %s", self)
