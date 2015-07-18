"""Core YAML mapping functionality."""

import os
import abc
import functools

import yaml

from . import common, exceptions, settings
from .bases import Container

MAPPER = 'yorm_mapper'

log = common.logger(__name__)


def get_mapper(obj):
    """Get `Mapper` instance attached to an object."""
    try:
        mapper = getattr(obj, MAPPER)
    except AttributeError:
        if isinstance(obj, (dict, list)):
            return None
        else:
            msg = "mapped {!r} missing {!r} attribute".format(obj, MAPPER)
            raise AttributeError(msg) from None
    else:
        return mapper


def set_mapper(obj, path, attrs, auto=True, root=None):
    """Create and attach a `Mapper` instance to an object."""
    mapper = Mapper(obj, path, attrs, auto=auto, root=root)
    setattr(obj, MAPPER, mapper)
    return mapper


def file_required(create=False):
    """Decorator for methods that require the file to exist.

    :param create: boolean or the method to decorate

    """
    def decorator(method):

        @functools.wraps(method)
        def wrapped(self, *args, **kwargs):  # pylint: disable=W0621
            if not self.path:
                return None
            if not self.exists and self.auto:
                if create is True and not self.deleted:
                    self.create()
                else:
                    msg = "cannot access deleted: {}".format(self.path)
                    raise exceptions.FileDeletedError(msg)
            return method(self, *args, **kwargs)

        return wrapped

    if callable(create):
        return decorator(create)
    else:
        return decorator


def prevent_recursion(method):
    """Decorator to prevent indirect recursive calls."""

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        # pylint: disable=W0212
        if self._activity:
            return
        self._activity = True
        result = method(self, *args, **kwargs)
        self._activity = False
        return result

    return wrapped


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

    def __init__(self, path, auto=True):
        self.path = path
        self.auto = auto
        self.auto_store = False
        self.exists = self.path and os.path.isfile(self.path)
        self.deleted = False
        self._activity = False
        self._timestamp = 0
        self._fake = ""

    def __str__(self):
        return str(self.path)

    @property
    def text(self):
        """Get file contents."""
        log.info("getting contents of %s...", prefix(self))
        if settings.fake:
            text = self._fake
        else:
            text = self._read()
        log.trace("text read: %r", text)
        return text

    @text.setter
    def text(self, text):
        """Set file contents."""
        log.info("setting contents of %s...", prefix(self))
        if settings.fake:
            self._fake = text
        else:
            self._write(text)
        log.trace("text wrote: %r", text)
        self.modified = True

    @property
    def modified(self):
        """Determine if the file has been modified."""
        if settings.fake:
            changes = self._timestamp is not None
            return changes
        elif not self.exists:
            return True
        else:
            was = self._timestamp
            now = common.stamp(self.path)
            return was != now

    @modified.setter
    def modified(self, changes):
        """Mark the file as modified if there are changes."""
        if changes:
            log.debug("marked %s as modified", prefix(self))
            self._timestamp = 0
        else:
            if settings.fake or self.path is None:
                self._timestamp = None
            else:
                self._timestamp = common.stamp(self.path)
            log.debug("marked %s as unmodified", prefix(self))

    def create(self, obj):
        """Create a new file for the object."""
        log.info("creating %s for %r...", prefix(self), obj)
        if self.exists:
            log.warning("already created: %s", self)
            return
        if not settings.fake:
            common.create_dirname(self.path)
            common.touch(self.path)
        self.exists = True
        self.deleted = False

    @file_required
    @prevent_recursion
    def fetch(self, obj, attrs):
        """Update the object's mapped attributes from its file."""
        log.info("fetching %r from %s...", obj, prefix(self))

        # Parse data from file
        text = self._read()
        data = self._load(text, self.path)
        log.trace("loaded: {}".format(data))

        # Update all attributes
        attrs2 = attrs.copy()
        for name, data in data.items():
            attrs2.pop(name, None)

            # Find a matching converter
            try:
                converter = attrs[name]
            except KeyError:
                # TODO: determine if runtime import is the best way to avoid
                # cyclic import
                from .converters import match
                converter = match(name, data)
                attrs[name] = converter

            # Convert the loaded attribute
            attr = getattr(obj, name, None)
            if all((isinstance(attr, converter),
                    issubclass(converter, Container))):
                attr.update_value(data)
            else:
                attr = converter.to_value(data)
                setattr(obj, name, attr)
            self._remap(attr)
            log.trace("value fetched: %s = %r", name, attr)

        # Add missing attributes
        for name, converter in attrs2.items():
            if not hasattr(obj, name):
                value = converter.to_value(None)
                msg = "fetched default value for missing attribute: %s = %r"
                log.warn(msg, name, value)
                setattr(obj, name, value)

        # Set meta attributes
        self.modified = False

    @file_required(create=True)
    @prevent_recursion
    def store(self, obj, attrs):
        """Format and save the object's mapped attributes to its file."""
        log.info("storing %r to %s...", obj, prefix(self))

        # Format the data items
        data = {}
        for name, converter in attrs.items():
            try:
                value = getattr(obj, name)
            except AttributeError:
                value = None
                msg = "storing default data for missing attribute '%s'..."
                log.warn(msg, name)

            data2 = converter.to_data(value)

            log.trace("data to store: %s = %r", name, data2)
            data[name] = data2

        # Dump data to file
        text = self._dump(data)
        self._write(text)

        # Set meta attributes
        self.modified = True
        self.auto_store = self.auto

    def delete(self):
        """Delete the object's file from the file system."""
        if self.exists:
            log.info("deleting %s...", prefix(self))
            if not settings.fake:
                common.delete(self.path)
        else:
            log.warning("already deleted: %s", self)
        self.exists = False
        self.deleted = True

    @file_required
    def _read(self):
        """Read text from the object's file.

        :param path: path to a text file

        :return: contexts of text file

        """
        if settings.fake:
            return self._fake
        elif not self.exists:
            return ""
        else:
            return common.read_text(self.path)

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

    @abc.abstractstaticmethod
    def _load(text, path):  # pragma: no cover (abstract method)
        """Parsed data from text.

        :param text: text read from a file
        :param path: path to the file (for displaying errors)

        :return: dictionary of parsed data

        """
        raise NotImplementedError

    @abc.abstractstaticmethod
    def _dump(data):  # pragma: no cover (abstract method)
        """Dump data to text.

        :param data: dictionary of data

        :return: text to write to a file

        """
        raise NotImplementedError

    def _remap(self, obj):
        """Restore mapping on nested attributes."""
        if isinstance(obj, Container):
            set_mapper(obj, None, common.attrs[obj.__class__], root=self)
            if isinstance(obj, dict):
                for obj2 in obj.values():
                    self._remap(obj2)
            else:
                assert isinstance(obj, list)
                for obj2 in obj:
                    self._remap(obj2)


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

    def __init__(self, obj, path, attrs, auto=True, root=None):
        super().__init__(path, auto=auto)
        self.obj = obj
        self.attrs = attrs
        self.root = root

    def create(self):  # pylint: disable=W0221
        super().create(self.obj)

    def fetch(self):  # pylint: disable=W0221
        if self.root and self.root.auto and not self._activity:
            self._activity = True
            self.root.fetch()
            self._activity = False
        super().fetch(self.obj, self.attrs)

    def store(self):  # pylint: disable=W0221
        if self.root and self.root.auto and not self._activity:
            self._activity = True
            self.root.store()
            self._activity = False
        super().store(self.obj, self.attrs)
