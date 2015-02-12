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

        FILE -> read -> [text] -> load -> [dict] -> retrieve -> ATTRIBUTES

    When settings an attribute:

        ATTRIBUTES -> store -> [dict] -> dump -> [text] -> write -> FILE

    After the mapped file is no longer needed:

        delete -> [null] -> FILE

    """

    def __init__(self, path):
        self.path = path
        self.auto = False
        self.exists = True
        self.retrieving = False
        self.storing = False
        # TODO: replace this variable with a timeout or modification check
        self.retrieved = False

    def __str__(self):
        return str(self.path)

    def create(self, obj):
        """Create a new file for the object."""
        log.critical((self.path, obj))
        if self._fake or not os.path.isfile(self.path):
            log.info("mapping %r to %s'%s'...", obj, self._fake, self)
            if not self._fake:
                common.create_dirname(self.path)
                common.touch(self.path)
        self.exists = True

    @readwrite
    def retrieve(self, obj):
        """Load the object's properties from its file."""
        if self.storing:
            return
        self.retrieving = True
        log.debug("retrieving %r from %s'%s'...", obj, self._fake, self.path)

        # Parse data from file
        if self._fake:
            text = getattr(obj, 'yorm_fake', "")
        else:
            text = self.read()
        data = self.load(text, self.path)
        log.trace("loaded: {}".format(data))

        # Update attributes
        for name, data in data.items():
            try:
                converter = obj.yorm_attrs[name]
            except KeyError:
                # TODO: determine if this runtime import is the best way to do this
                from . import standard
                converter = standard.match(name, data)
                obj.yorm_attrs[name] = converter
            value = converter.to_value(data)
            log.trace("value retrieved: '{}' = {}".format(name, repr(value)))
            setattr(obj, name, value)

        # Set meta attributes
        self.retrieving = False
        self.retrieved = True

    @readwrite
    def read(self):
        """Read text from the object's file.

        :param path: path to a text file

        :return: contexts of text file

        """
        return common.read_text(self.path)

    @staticmethod
    def load(text, path):
        """Load YAML data from text.

        :param text: text read from a file
        :param path: path to the file (for displaying errors)

        :return: dictionary of YAML data

        """
        return common.load_yaml(text, path)

    @readwrite
    def store(self, obj):
        """Format and save the object's properties to its file."""
        if self.retrieving:
            return
        self.storing = True
        log.debug("storing %r to %s'%s'...", obj, self._fake, self.path)

        # Format the data items
        data = {}
        for name, converter in obj.yorm_attrs.items():
            try:
                value = getattr(obj, name)
            except AttributeError as exc:
                log.debug(exc)
                value = None
            data2 = converter.to_data(value)
            log.trace("data to store: '%s' = %r", name, data2)
            data[name] = data2

        # Dump data to file
        text = self.dump(data)
        if self._fake:
            obj.yorm_fake = text
        else:
            self.write(text)

        # Set meta attributes
        self.storing = False

    @staticmethod
    def dump(data):
        """Dump YAML data to text.

        :param data: dictionary of YAML data

        :return: text to write to a file

        """
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)

    @readwrite
    def write(self, text):
        """Write text to the object's file.

        :param text: text to write to a file
        :param path: path to the file

        """
        common.write_text(text, self.path)

    def delete(self):
        """Delete the object's file from the file system."""
        if self.exists:
            log.info("deleting %s'%s'...", self._fake, self.path)
            if not self._fake:
                common.delete(self.path)
            self.retrieved = False
            self.exists = False
        else:
            log.warning("already deleted: %s", self)

    @property
    def _fake(self):  # pylint: disable=R0201
        """Return a string indicating the fake setting to use in logging."""
        return "(fake) " if settings.fake else ''
