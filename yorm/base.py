"""Base classes."""

import os
import abc

import yaml

from . import common

log = common.logger(__name__)


class Mappable(metaclass=abc.ABCMeta):  # pylint:disable=R0921

    """Base class for objects with attributes that map to YAML."""

    auto = True  # set to False to delay automatic save until explicit save

    def __init__(self):
        self.path = None
        self.root = None
        self._data = {}
        self._exists = True
        self._loaded = False
        # Set default values
        for name, converter in self.__mapping__.items():
            self._data[name] = converter.to_value(None)
        self.save()

    def __getattribute__(self, name):
        if name not in ('__mapping__', 'load', '_data') \
                and name in self.__mapping__:
            self.load()
            return self._data[name]
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in self.__mapping__:
            self._data[name] = value
            self.save()
        super().__setattr__(name, value)

    @staticmethod
    def _create(path, name):  # pragma: no cover (integration test)
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

    def load(self, reload=False):
        """Load the object's properties from its file."""
        if self._loaded and not reload:
            return
        log.debug("loading {}...".format(repr(self)))
        # Read text from file
        text = self._read(self.path)
        # Parse YAML data from text
        data = self._load(text, self.path)
        # Store parsed data
        for key, data in data.items():
            try:
                converter = self.__mapping__[key]
            # TODO: remove this block after deleting self._data
            except KeyError:  # pragma: no cover (temporary)
                continue
            else:
                value = converter.to_value(data)
                self._data[key] = value
        # Set meta attributes
        self._loaded = True

    def _read(self, path):  # pragma: no cover (integration test)
        """Read text from the object's file.

        :param path: path to a text file

        :return: contexts of text file

        """
        if not self._exists:
            msg = "cannot read from deleted: {}".format(self.path)
            raise FileNotFoundError(msg)
        return common.read_text(path)

    @staticmethod
    def _load(text, path):
        """Load YAML data from text.

        :param text: text read from a file
        :param path: path to the file (for displaying errors)

        :return: dictionary of YAML data

        """
        return common.load_yaml(text, path)

    def save(self):
        """Format and save the object's properties to its file."""
        log.debug("saving {}...".format(repr(self)))
        # Format the data items
        data = {}
        for key, value in self._data.items():
            try:
                converter = self.__mapping__[key]
            # TODO: remove this block after deleting self._data
            except KeyError:  # pragma: no cover (temporary)
                continue
            else:
                data2 = converter.to_data(value)
                data[key] = data2
        # Dump the data to YAML
        text = self._dump(data)
        # Save the YAML to file
        self._write(text, self.path)
        # Set meta attributes
        self._loaded = False
        self.auto = True

    def _write(self, text, path):  # pragma: no cover (integration test)
        """Write text to the object's file.

        :param text: text to write to a file
        :param path: path to the file

        """
        if not self._exists:
            raise FileNotFoundError("cannot save to deleted: {}".format(self))
        common.write_text(text, path)

    @staticmethod
    def _dump(data):
        """Dump YAML data to text.

        :param data: dictionary of YAML data

        :return: text to write to a file

        """
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)


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
