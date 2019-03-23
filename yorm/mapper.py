"""Core object-file mapping functionality."""

import functools
from pprint import pformat
import logging

from . import common, diskutils, exceptions, types, settings
from .bases import Container

log = logging.getLogger(__name__)


def file_required(method):
    """Decorate methods that require the file to exist."""

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        if self.deleted:
            msg = "File deleted: {}".format(self.path)
            raise exceptions.DeletedFileError(msg)
        if self.missing and not settings.fake:
            msg = "File missing: {}".format(self.path)
            raise exceptions.MissingFileError(msg)
        return method(self, *args, **kwargs)

    return wrapped


def prevent_recursion(method):
    """Decorate methods to prevent indirect recursive calls."""

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        # pylint: disable=protected-access
        if self._activity:
            return None
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

        FILE -> read -> [text] -> parse -> [dict] -> load -> ATTRIBUTES

    When setting an attribute:

        ATTRIBUTES -> save -> [dict] -> dump -> [text] -> write -> FILE

    After the mapped file is no longer needed:

        delete -> [null] -> FILE

    """

    def __init__(self, obj, path, attrs, *,
                 auto_create=True, auto_save=True,
                 auto_track=False, auto_resolve=False):
        self._obj = obj
        self.path = path
        self.attrs = attrs
        self.auto_create = auto_create
        self.auto_save = auto_save
        self.auto_track = auto_track
        self.auto_resolve = auto_resolve

        self.exists = diskutils.exists(self.path)
        self.deleted = False
        self.auto_save_after_load = False

        self._activity = False
        self._timestamp = 0
        self._fake = ""

    def __str__(self):
        return str(self.path)

    @property
    def missing(self):
        return not self.exists

    @property
    def modified(self):
        """Determine if the file has been modified."""
        if settings.fake:
            changes = self._timestamp is not None
            return changes
        elif not self.exists:
            return True
        else:
            # TODO: this raises an exception is the file is missing
            was = self._timestamp
            now = diskutils.stamp(self.path)
            return was != now

    @modified.setter
    @file_required
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
    def text(self):
        """Get file contents as a string."""
        log.info("Getting contents of %s...", prefix(self))
        if settings.fake:
            text = self._fake
        else:
            text = self._read()
        log.trace("Text read: \n%s", text[:-1])
        return text

    @text.setter
    def text(self, text):
        """Set file contents from a string."""
        log.info("Setting contents of %s...", prefix(self))
        if settings.fake:
            self._fake = text
        else:
            self._write(text)
        log.trace("Text wrote: \n%s", text.rstrip())
        self.modified = True

    @property
    def data(self):
        """Get the file values as a dictionary."""
        text = self._read()
        try:
            data = diskutils.parse(text, self.path)
        except ValueError as e:
            if not self.auto_resolve:
                raise e from None

            log.debug(e)
            log.warning("Clearing invalid contents: %s", self.path)
            self._write("")
            return {}

        log.trace("Parsed data: \n%s", pformat(data))
        return data

    @data.setter
    def data(self, data):
        """Set the file values from a dictionary."""
        text = diskutils.dump(data, self.path)
        self._write(text)

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
    def load(self):
        """Update the object's mapped attributes from its file."""
        log.info("Loading %r from %s...", self._obj, prefix(self))

        # Update all attributes
        attrs2 = self.attrs.copy()
        for name, data in self.data.items():
            attrs2.pop(name, None)

            # Find a matching converter
            try:
                converter = self.attrs[name]
            except KeyError:
                if self.auto_track:
                    converter = types.match(name, data)
                    self.attrs[name] = converter
                else:
                    msg = "Ignored unknown file attribute: %s = %r"
                    log.warning(msg, name, data)
                    continue

            # Convert the parsed value to the attribute's final type
            attr = getattr(self._obj, name, None)
            if isinstance(attr, converter) and \
                    issubclass(converter, Container):
                attr.update_value(data, auto_track=self.auto_track)
            else:
                log.trace("Converting attribute %r using %r", name, converter)
                attr = converter.to_value(data)
                setattr(self._obj, name, attr)
            self._remap(attr, self)
            log.trace("Value loaded: %s = %r", name, attr)

        # Add missing attributes
        for name, converter in attrs2.items():
            try:
                existing_attr = getattr(self._obj, name)
            except AttributeError:
                value = converter.create_default()
                msg = "Default value for missing object attribute: %s = %r"
                log.warning(msg, name, value)
                setattr(self._obj, name, value)
                self._remap(value, self)
            else:
                if issubclass(converter, Container):
                    if isinstance(existing_attr, converter):
                        pass  # TODO: Update 'existing_attr' values to replace None values
                    else:
                        msg = "Converting container attribute %r using %r"
                        log.trace(msg, name, converter)
                        value = converter.create_default()
                        setattr(self._obj, name, value)
                        self._remap(value, self)
                else:
                    pass  # TODO: Figure out when this case occurs

        # Set meta attributes
        self.modified = False

    def _remap(self, obj, root):
        """Attach mapper on nested attributes."""
        if isinstance(obj, Container):
            common.set_mapper(obj, root)

            if isinstance(obj, dict):
                for obj2 in obj.values():
                    self._remap(obj2, root)
            else:
                assert isinstance(obj, list)
                for obj2 in obj:
                    self._remap(obj2, root)

    @file_required
    @prevent_recursion
    def save(self):
        """Format and save the object's mapped attributes to its file."""
        log.info("Saving %r to %s...", self._obj, prefix(self))

        # Format the data items
        data = self.attrs.__class__()
        for name, converter in self.attrs.items():
            try:
                value = getattr(self._obj, name)
            except AttributeError:
                data2 = converter.to_data(None)
                msg = "Default data for missing object attribute: %s = %r"
                log.warning(msg, name, data2)
            else:
                data2 = converter.to_data(value)

            log.trace("Data to save: %s = %r", name, data2)
            data[name] = data2

        # Save the formatted to disk
        self.data = data

        # Set meta attributes
        self.modified = True
        self.auto_save_after_load = self.auto_save

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
