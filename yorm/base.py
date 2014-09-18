"""Base classes."""

import os
import abc
import functools

import yaml

from . import common

log = common.logger(__name__)


class Mappable(metaclass=abc.ABCMeta):  # pylint:disable=R0921

    """Base class for objects with attributes that map to YAML."""

    def __getattribute__(self, name):
        if name in ('yorm_mapper', 'yorm_attrs'):
            return object.__getattribute__(self, name)

        log.trace("getting attribute '{}'...".format(name))

        if name in self.yorm_attrs:
            self.yorm_mapper.retrieve(self)
        else:
            log.trace("unmapped: {}".format(name))

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        log.trace("setting attribute '{}' to {}...".format(name, repr(value)))

        if hasattr(self, 'yorm_attrs') and name in self.yorm_attrs:
            converter = self.yorm_attrs[name]
            value = converter.to_value(value)

        object.__setattr__(self, name, value)

        if hasattr(self, 'yorm_attrs') and name in self.yorm_attrs:
            if hasattr(self, 'yorm_mapper') and self.yorm_mapper.auto:
                self.yorm_mapper.store(self)
            else:
                log.trace("automatic storage is off")
        else:
            log.trace("unmapped: {}".format(name))

    def __enter__(self):
        log.debug("turning off automatic storage...")
        self.yorm_mapper.auto = False

    def __exit__(self, *_):
        log.debug("turning on automatic storage...")
        self.yorm_mapper.store(self)


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

    """Utility class to manipulate YAML files."""

    def __init__(self, path):
        self.path = path
        self.auto = True
        self.exists = True
        self.retrieving = False
        self.storing = False
        # TODO: replace this variable with a timeout or modification check
        self.retrieved = False

    def __str__(self):
        return str(self.path)

    def create(self, obj):
        """Create a new file for the object."""
        if not os.path.exists(self.path):
            log.debug("creating '{}' for {}...".format(self, repr(obj)))
            common.create_dirname(self.path)
            common.touch(self.path)
            self.exists = True

    @readwrite
    def retrieve(self, obj):
        """Load the object's properties from its file."""
        if self.storing:
            log.trace("storing in process...")
            return
        self.retrieving = True
        log.debug("retrieving {} from {}...".format(repr(obj), self))

        # Parse data from file
        text = self.read()
        data = self.load(text, self.path)
        log.trace("loaded: {}".format(data))

        # Update attributes
        for key, data in data.items():
            try:
                converter = obj.yorm_attrs[key]
            except KeyError:
                # TODO: determine if this runtime import is the best way to do this
                from . import standard
                converter = standard.match(data)
                log.info("new attribute: {}".format(key))
                obj.yorm_attrs[key] = converter
            value = converter.to_value(data)
            log.trace("value retrieved: {} = {}".format(key, repr(value)))
            setattr(obj, key, value)

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
            log.trace("retrieving in process...")
            return
        self.storing = True
        log.debug("storing {} to {}...".format(repr(obj), self))

        # Format the data items
        data = {}
        for name, converter in obj.yorm_attrs.items():
            value = getattr(obj, name, None)
            data2 = converter.to_data(value)
            log.debug("data to store: {} = {}".format(name, repr(data2)))
            data[name] = data2

        # Dump data to file
        text = self.dump(data)
        self.write(text)

        # Set meta attributes
        self.storing = False
        self.auto = True

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
            log.info("deleting '{}'...".format(self))
            common.delete(self.path)
            self.retrieved = False
            self.exists = False
        else:
            log.warning("already deleted: {}".format(self))


class Converter(metaclass=abc.ABCMeta):  # pylint:disable=R0921

    """Base class for attribute converters."""

    type = None

    @staticmethod
    @abc.abstractmethod
    def to_value(data):  # pylint: disable=E0213
        """Convert the loaded value back to its original attribute type."""
        raise NotImplementedError("method must be implemneted in subclasses")

    @staticmethod
    @abc.abstractmethod
    def to_data(value):  # pylint: disable=E0213
        """Convert the attribute's value for optimal dumping to YAML."""
        raise NotImplementedError("method must be implemneted in subclasses")


class ContainerMeta(type):

    """Metaclass to initialize `yorm_attrs` on class declaration."""

    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        cls.yorm_attrs = {}


class Dictionary(metaclass=ContainerMeta):

    """Base class for a dictionary of attribute converters."""

    @classmethod
    def to_value(cls, data):  # pylint: disable=E0213
        """Convert all loaded values back to its original attribute types."""
        if cls is Dictionary:
            msg = "Dictionary class must be subclassed to use"
            raise NotImplementedError(msg)

        value = {}

        yorm_attrs = cls.yorm_attrs.copy()

        for name, data in cls.to_dict(data).items():
            try:
                converter = yorm_attrs.pop(name)
            except KeyError:
                from . import standard
                converter = standard.match(data)
                log.info("new attribute: {}".format(name))
                cls.yorm_attrs[name] = converter
            value[name] = converter.to_value(data)

        for name, converter in yorm_attrs.items():
            log.debug("adding deleted '{}'...".format(name))
            value[name] = converter.to_value(None)

        return value

    @classmethod
    def to_data(cls, value):  # pylint: disable=E0213
        """Convert all attribute values for optimal dumping to YAML."""
        if cls is Dictionary:
            msg = "Dictionary class must be subclassed to use"
            raise NotImplementedError(msg)

        data = {}

        for name, converter in cls.yorm_attrs.items():
            data[name] = converter.to_data(value.get(name, None))

        return data

    @staticmethod
    def to_dict(obj):
        """Convert a dictionary-like object to a dictionary.

        >>> Dictionary.to_dict({'key': 42})
        {'key': 42}

        >>> Dictionary.to_dict("key=42")
        {'key': '42'}

        >>> Dictionary.to_dict("key")
        {'key': None}

        >>> Dictionary.to_dict(None)
        {}

        """
        if isinstance(obj, dict):
            return obj
        elif isinstance(obj, str):
            text = obj.strip()
            parts = text.split('=')
            if len(parts) == 2:
                return {parts[0]: parts[1]}
            else:
                return {text: None}
        else:
            return {}


class classproperty(object):

    """Read-only class property decorator."""

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class List(metaclass=ContainerMeta):

    """Base class for a homogeneous list of attribute converters."""

    ALL = 'all'

    @classproperty
    def item_type(cls):
        return cls.yorm_attrs.get(cls.ALL)

    @classmethod
    def to_value(cls, data):  # pylint: disable=E0213
        """Convert all loaded values back to the original attribute type."""
        if cls is List:
            raise NotImplementedError("List class must be subclassed to use")
        if not cls.item_type:
            raise NotImplementedError("List subclass must specify item type")

        if isinstance(data, list):
            return data
        elif isinstance(data, str):
            text = data.strip()
            if ',' in text and ' ' not in text:
                return text.split(',')
            else:
                return text.split()
        elif data is not None:
            return [data]
        else:
            return []

    @classmethod
    def to_data(cls, value):  # pylint: disable=E0213
        """Convert all attribute values for optimal dumping to YAML."""
        if cls is List:
            raise NotImplementedError("List class must be subclassed to use")
        if not cls.item_type:
            raise NotImplementedError("List subclass must specify item type")

        return value
