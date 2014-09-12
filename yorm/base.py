"""Base classes."""

import os
import abc

import yaml

from . import common

log = common.logger(__name__)


class Mappable(metaclass=abc.ABCMeta):  # pylint:disable=R0921

    """Base class for objects with attributes that map to YAML."""

    auto = False  # set to False to delay automatic save until explicit save

    _exists = True
    _retrieving = False
    _storing = False
    _retrieved = False

    def __getattribute__(self, name):
        if name in ('yorm_attrs', 'yorm_mapper', 'auto'):
            return object.__getattribute__(self, name)
        if name in self.yorm_attrs:
            if self.auto:
                log.debug("retrieving: {}".format(name))
                self.yorm_mapper.retrieve(self)
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name in self.yorm_attrs:
            if self.auto:
                log.debug("storing: {} ({})".format(name, value))
                self.yorm_mapper.store(self)


class Mapper:

    """Utility class to manipulate YAML files."""

    @staticmethod
    def create(path, name):  # pragma: no cover (integration test)
        """Create a new file for the object.

        :param path: path to new file
        :param name: humanized name for this file

        :raises: :class:`~doorstop.common.DoorstopError` if the file
            already exists

        """
        if os.path.exists(path):
            raise FileExistsError("{} already exists: {}".format(name, path))
        common.create_dirname(path)
        common.touch(path)

    def retrieve(self, obj, reload=False):
        """Load the object's properties from its file."""
        if obj._retrieved and not reload:
            return
        if obj._storing:
            log.trace("storing in process...")
            return
        log.debug("retrieving {}...".format(repr(self)))
        obj._retrieving = True
        # Read text from file
        text = self.read(obj)
        # Parse YAML data from text
        data = self.load(text, obj.yorm_path)
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
        obj._retrieving = False
        obj._retrieved = True

    @staticmethod
    def read(obj):  # pragma: no cover (integration test)
        """Read text from the object's file.

        :param path: path to a text file

        :return: contexts of text file

        """
        if not obj._exists:
            msg = "cannot read from deleted: {}".format(obj.yorm_path)
            raise FileNotFoundError(msg)
        return common.read_text(obj.yorm_path)

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
        if obj._retrieving:
            log.trace("retrieving in process...")
            return
        obj._storing = True
        log.debug("storing {}...".format(repr(self)))
        # Format the data items
        data = {}
        for name, converter in obj.yorm_attrs.items():
            value = getattr(obj, name)
            data2 = converter.to_data(value)
            data[name] = data2
        log.debug("data to store: {}".format(data))
        # Dump the data to YAML
        text = self.dump(data)
        # Save the YAML to file
        self.write(obj, text)
        # Set meta attributes
        obj._storing = False
        obj._retrieved = False
        obj.auto = True

    @staticmethod
    def dump(data):
        """Dump YAML data to text.

        :param data: dictionary of YAML data

        :return: text to write to a file

        """
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)

    @staticmethod
    def write(obj, text):  # pragma: no cover (integration test)
        """Write text to the object's file.

        :param text: text to write to a file
        :param path: path to the file

        """
        if not obj._exists:
            raise FileNotFoundError("cannot save to deleted: {}".format(obj))
        common.write_text(text, obj.yorm_path)

    # TODO: add a test for delete
    def delete(self, obj):  # pragma: no cover (integration test)
        """Delete the object's file from the file system."""
        if obj._exists:
            log.info("deleting {}...".format(self))
            common.delete(obj.yorm_path)
            obj._retrieved = False  # force the object to reload
            obj._exists = False  # but, prevent future access
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
