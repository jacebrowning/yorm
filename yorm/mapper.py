"""Core object-file mapping functionality."""

import os
import functools
from pprint import pformat

from . import common, diskutils, exceptions, settings
from .bases import Container

MAPPER = '__mapper__'

log = common.logger(__name__)


def get_mapper(obj):
    """Get `Mapper` instance attached to an object."""
    try:
        return object.__getattribute__(obj, MAPPER)
    except AttributeError:
        return None


def set_mapper(obj, path, attrs, auto=True):
    """Create and attach a `Mapper` instance to an object."""
    mapper = Mapper(obj, path, attrs, auto=auto)
    setattr(obj, MAPPER, mapper)
    return mapper


def file_required(create=False):
    """Decorator for methods that require the file to exist.

    :param create: boolean or the method to decorate

    """
    def decorator(method):

        @functools.wraps(method)
        def wrapped(self, *args, **kwargs):
            if not self.exists and self.auto:
                if create is True and not self.deleted:
                    self.create()
                else:
                    msg = "Cannot access deleted: {}".format(self.path)
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
        # pylint: disable=protected-access
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


class Mapper:
    """Utility class to map an object's attributes to a file.

    To start mapping attributes to a file:

        create -> [empty] -> FILE

    When getting an attribute:

        FILE -> read -> [text] -> load -> [dict] -> fetch -> ATTRIBUTES

    When setting an attribute:

        ATTRIBUTES -> store -> [dict] -> dump -> [text] -> write -> FILE

    After the mapped file is no longer needed:

        delete -> [null] -> FILE

    """

    def __init__(self, obj, path, attrs, auto=True):
        self._obj = obj
        self.path = path
        self.attrs = attrs
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
        log.info("Getting contents of %s...", prefix(self))
        if settings.fake:
            text = self._fake
        else:
            text = self._read()
        log.trace("Text read: \n%s", text[:-1])
        return text

    @text.setter
    def text(self, text):
        """Set file contents."""
        log.info("Setting contents of %s...", prefix(self))
        if settings.fake:
            self._fake = text
        else:
            self._write(text)
        log.trace("Text wrote: \n%s", text[:-1])
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
            now = diskutils.stamp(self.path)
            return was != now

    @modified.setter
    def modified(self, changes):
        """Mark the file as modified if there are changes."""
        if changes:
            log.debug("Marked %s as modified", prefix(self))
            self._timestamp = 0
        else:
            if settings.fake or self.path is None:
                self._timestamp = None
            else:
                self._timestamp = diskutils.stamp(self.path)
            log.debug("Marked %s as unmodified", prefix(self))

    @property
    def ext(self):
        if '.' in self.path:
            return self.path.split('.')[-1]
        else:
            return 'yml'

    def create(self):
        """Create a new file for the object."""
        log.info("Creating %s for %r...", prefix(self), self._obj)
        if self.exists:
            log.warning("Already created: %s", self)
            return
        if not settings.fake:
            diskutils.touch(self.path)
        self.exists = True
        self.deleted = False

    @file_required
    @prevent_recursion
    def fetch(self):
        """Update the object's mapped attributes from its file."""
        log.info("Fetching %r from %s...", self._obj, prefix(self))

        # Parse data from file
        text = self._read()
        data = diskutils.load(text=text, path=self.path, ext=self.ext)
        log.trace("Loaded data: \n%s", pformat(data))

        # Update all attributes
        attrs2 = self.attrs.copy()
        for name, data in data.items():
            attrs2.pop(name, None)

            # Find a matching converter
            try:
                converter = self.attrs[name]
            except KeyError:
                # TODO: determine if runtime import is the best way to avoid
                # cyclic import
                from .types import match
                converter = match(name, data)
                self.attrs[name] = converter

            # Convert the loaded attribute
            attr = getattr(self._obj, name, None)
            if all((isinstance(attr, converter),
                    issubclass(converter, Container))):
                attr.update_value(data)
            else:
                attr = converter.to_value(data)
                setattr(self._obj, name, attr)
            self._remap(attr, self)
            log.trace("Value fetched: %s = %r", name, attr)

        # Add missing attributes
        for name, converter in attrs2.items():
            if not hasattr(self._obj, name):
                value = converter.to_value(None)
                msg = "Fetched default value for missing attribute: %s = %r"
                log.warning(msg, name, value)
                setattr(self._obj, name, value)

        # Set meta attributes
        self.modified = False

    @file_required(create=True)
    @prevent_recursion
    def store(self):
        """Format and save the object's mapped attributes to its file."""
        log.info("Storing %r to %s...", self._obj, prefix(self))

        # Format the data items
        data = {}
        for name, converter in self.attrs.items():
            try:
                value = getattr(self._obj, name)
            except AttributeError:
                value = None
                msg = "Storing default data for missing attribute '%s'..."
                log.warning(msg, name)

            data2 = converter.to_data(value)

            log.trace("Data to store: %s = %r", name, data2)
            data[name] = data2

        # Dump data to file
        text = diskutils.dump(data=data, ext=self.ext)
        self._write(text)

        # Set meta attributes
        self.modified = True
        self.auto_store = self.auto

    def delete(self):
        """Delete the object's file from the file system."""
        if self.exists:
            log.info("Deleting %s...", prefix(self))
            diskutils.delete(self.path)
        else:
            log.warning("Already deleted: %s", self)
        self.exists = False
        self.deleted = True

    @file_required
    def _read(self):
        """Read text from the object's file."""
        if settings.fake:
            return self._fake
        elif not self.exists:
            return ""
        else:
            return diskutils.read(self.path)

    @file_required
    def _write(self, text):
        """Write text to the object's file."""
        if settings.fake:
            self._fake = text
        else:
            diskutils.write(text, self.path)

    def _remap(self, obj, root):
        """Restore mapping on nested attributes."""
        if isinstance(obj, Container):
            setattr(obj, MAPPER, root)

            if isinstance(obj, dict):
                for obj2 in obj.values():
                    self._remap(obj2, root)
            else:
                assert isinstance(obj, list)
                for obj2 in obj:
                    self._remap(obj2, root)
