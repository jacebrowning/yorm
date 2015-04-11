"""Core YAML mapping functionality."""

import os
import abc
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


def prefix(obj):
    """Prefix a string with a fake designator if enabled."""
    fake = "(fake) " if settings.fake else ""
    name = obj if isinstance(obj, str) else "'{}'".format(obj)
    return fake + name


class BaseHelper(metaclass=abc.ABCMeta):

    """Utility class to map attributes to text files.

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
        self._fake = None

    def __str__(self):
        return str(self.path)

    @property
    def text(self):
        """Get fake file contents (if enabled)."""
        if settings.fake:
            return self._fake
        else:
            return self._read()

    @text.setter
    def text(self, text):
        """Set fake file contents (if enabled)."""
        if settings.fake:
            self._fake = text
        else:
            self._write(text)
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
                # TODO: determine if runtime import is the best way to avoid cyclic import
                from .converters import match
                converter = match(name, data)
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
            return self._fake
        else:
            return common.read_text(self.path)

    @abc.abstractstaticmethod
    def _load(text, path):  # pragma: no cover (abstract method)
        """Parsed data from text.

        :param text: text read from a file
        :param path: path to the file (for displaying errors)

        :return: dictionary of parsed data

        """
        raise NotImplementedError

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

    @abc.abstractstaticmethod
    def _dump(data):  # pragma: no cover (abstract method)
        """Dump data to text.

        :param data: dictionary of data

        :return: text to write to a file

        """
        raise NotImplementedError

    @file_required
    def _write(self, text):
        """Write text to the object's file.

        :param text: text to write to a file
        :param path: path to the file

        """
        if settings.fake:
            self._fake = text
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


class Helper(BaseHelper):

    """Utility class to map attributes to YAML files."""

    @staticmethod
    def _load(text, path):
        """Load YAML data from text.

        :param text: text read from a file
        :param path: path to the file (for displaying errors)

        :return: dictionary of YAML data

        """
        return common.load_yaml(text, path)

    @staticmethod
    def _dump(data):
        """Dump YAML data to text.

        :param data: dictionary of YAML data

        :return: text to write to a file

        """
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)


class Mapper(Helper):

    """Maps an object's attribute to YAML files."""

    def __init__(self, obj, path, attrs):
        super().__init__(path)
        self.obj = obj
        self.attrs = attrs

    def create(self):  # pylint: disable=W0221
        return super().create(self.obj)

    @file_required
    def fetch(self, force=False):  # pylint: disable=W0221
        return super().fetch(self.obj, self.attrs, force=force)

    @file_required
    def store(self):  # pylint: disable=W0221
        return super().store(self.obj, self.attrs)
