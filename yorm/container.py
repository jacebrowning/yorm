"""Converter classes for abstract container types."""

import abc

from . import common
from . import standard

log = common.logger(__name__)


class ContainerMeta(abc.ABCMeta):

    """Metaclass to initialize `yorm_attrs` on class declaration."""

    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        cls.yorm_attrs = {}


class Dictionary(dict, metaclass=ContainerMeta):

    """Base class for a dictionary of attribute converters."""

    @classmethod
    def default(cls):
        """Create an uninitialized object."""
        if cls is Dictionary:
            msg = "Dictionary class must be subclassed to use"
            raise NotImplementedError(msg)

        return dict()

    @classmethod
    def to_value(cls, obj):  # pylint: disable=E0213
        """Convert all loaded values back to its original attribute types."""
        value = cls.default()

        # Convert object attributes to a dictionary
        yorm_attrs = cls.yorm_attrs.copy()
        if isinstance(obj, cls):
            items = obj.__dict__.items()
            dictionary = {k: v for k, v in items if k in yorm_attrs}
        else:
            dictionary = cls.to_dict(obj)

        # Map object attributes to converters
        for name, data in dictionary.items():
            try:
                converter = yorm_attrs.pop(name)
            except KeyError:
                converter = standard.match(name, data, nested=True)
                cls.yorm_attrs[name] = converter
            value[name] = converter.to_value(data)

        # Create default values for unmapped converters
        for name, converter in yorm_attrs.items():
            log.trace("adding missing nested key '{}'...".format(name))
            value[name] = converter.to_value(None)

        return value

    @classmethod
    def to_data(cls, obj):  # pylint: disable=E0213
        """Convert all attribute values for optimal dumping to YAML."""
        value = cls.to_value(obj)

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


class List(list, metaclass=ContainerMeta):

    """Base class for a homogeneous list of attribute converters."""

    ALL = 'all'

    @classmethod
    def default(cls):
        """Create an uninitialized object."""
        if cls is List:
            raise NotImplementedError("List class must be subclassed to use")
        if not cls.item_type:
            raise NotImplementedError("List subclass must specify item type")

        return cls.__new__(cls)

    @common.classproperty
    def item_type(cls):  # pylint: disable=E0213
        """Get the converter class for all items."""
        return cls.yorm_attrs.get(cls.ALL)

    @classmethod
    def to_value(cls, obj):  # pylint: disable=E0213
        """Convert all loaded values back to the original attribute type."""
        value = cls.default()

        for item in cls.to_list(obj):
            value.append(cls.item_type.to_value(item))

        return value

    @classmethod
    def to_data(cls, obj):  # pylint: disable=E0213
        """Convert all attribute values for optimal dumping to YAML."""
        value = cls.to_value(obj)

        data = []

        for item in value:
            data.append(cls.item_type.to_data(item))

        return data

    @staticmethod
    def to_list(obj):
        """Convert a list-like object to a list.

        >>> List.to_list([1, 2, 3])
        [1, 2, 3]

        >>> List.to_list("a,b,c")
        ['a', 'b', 'c']

        >>> List.to_list("item")
        ['item']

        >>> List.to_list(None)
        []

        """
        if isinstance(obj, list):
            return obj
        elif isinstance(obj, str):
            text = obj.strip()
            if ',' in text and ' ' not in text:
                return text.split(',')
            else:
                return text.split()
        elif obj is not None:
            return [obj]
        else:
            return []
