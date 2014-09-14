"""Base classes."""

import os
import abc

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


class Mapper:

    """Utility class to manipulate YAML files."""

    def __init__(self, path):
        self.path = path
        self.auto = True
        self.exists = True
        self.retrieved = False
        self.storing = False

    def __str__(self):
        return str(self.path)

    def create(self, obj):
        """Create a new file for the object."""
        if not os.path.exists(self.path):
            log.debug("creating '{}' for {}...".format(self, repr(obj)))
            common.create_dirname(self.path)
            common.touch(self.path)
            self.exists = True

    def retrieve(self, obj):
        """Load the object's properties from its file."""
        if self.storing:
            log.trace("storing in process...")
            return
        log.debug("retrieving {} from {}...".format(repr(obj), self))
        # Read text from file
        text = self.read()
        # Parse YAML data from text
        data = self.load(text, self.path)
        log.trace("loaded: {}".format(data))
        # Store parsed data
        for key, data in data.items():
            try:
                converter = obj.yorm_attrs[key]
            # TODO: add new attributes from the file (#12)
            except KeyError:  # pragma: no cover (temporary)
                continue
            else:
                value = converter.to_value(data)
                setattr(obj, key, value)
        # Set meta attributes
        self.retrieved = True

    def read(self):
        """Read text from the object's file.

        :param path: path to a text file

        :return: contexts of text file

        """
        if not self.exists:
            msg = "cannot read from deleted: {}".format(self.path)
            raise FileNotFoundError(msg)
        return common.read_text(self.path)

    @staticmethod
    def load(text, path):
        """Load YAML data from text.

        :param text: text read from a file
        :param path: path to the file (for displaying errors)

        :return: dictionary of YAML data

        """
        return common.load_yaml(text, path)

    def store(self, obj):
        """Format and save the object's properties to its file."""
        log.debug("storing {} to {}...".format(repr(obj), self))
        self.storing = True
        # Format the data items
        data = {}
        for name, converter in obj.yorm_attrs.items():
            value = getattr(obj, name, None)
            data2 = converter.to_data(value)
            data[name] = data2
        log.debug("data to store: {}".format(data))
        # Dump the data to YAML
        text = self.dump(data)
        # Save the YAML to file
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

    def write(self, text):
        """Write text to the object's file.

        :param text: text to write to a file
        :param path: path to the file

        """
        if not self.exists:
            msg = "cannot save to deleted: {}".format(self.path)
            raise FileNotFoundError(msg)
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

    @staticmethod
    @abc.abstractmethod
    def to_value(data):
        """Convert the loaded value back to its original attribute type."""

    @staticmethod
    @abc.abstractmethod
    def to_data(value):
        """Convert the attribute's value for optimal dumping to YAML."""
