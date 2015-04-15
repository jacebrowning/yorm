"""Converter classes for abstract container types."""

from .. import common
from ..base.convertible import Convertible
from . import standard

log = common.logger(__name__)


class Dictionary(Convertible, dict):

    """Base class for a dictionary of attribute converters."""

    @classmethod
    def default(cls):
        """Create an uninitialized object."""
        if cls is Dictionary:
            msg = "Dictionary class must be subclassed to use"
            raise NotImplementedError(msg)

        return cls.__new__(cls)

    @classmethod
    def to_value(cls, obj):  # pylint: disable=E0213
        """Convert all loaded values back to its original attribute types."""
        value = cls.default()

        # Convert object attributes to a dictionary
        attrs = common.ATTRS[cls].copy()
        if isinstance(obj, cls):
            dictionary = {}
            for k, v in obj.items():
                if k in attrs:
                    dictionary[k] = v
            for k, v in obj.__dict__.items():
                if k in attrs:
                    dictionary[k] = v
        else:
            dictionary = cls.to_dict(obj)

        # Map object attributes to converters
        for name, data in dictionary.items():
            try:
                converter = attrs.pop(name)
            except KeyError:
                converter = standard.match(name, data, nested=True)
                common.ATTRS[cls][name] = converter
            value[name] = converter.to_value(data)

        # Create default values for unmapped converters
        for name, converter in attrs.items():
            value[name] = converter.to_value(None)
            log.warn("added missing nested key '%s'...", name)

        return value

    @classmethod
    def to_data(cls, obj):  # pylint: disable=E0213
        """Convert all attribute values for optimal dumping to YAML."""
        value = cls.to_value(obj)

        data = {}

        for name, converter in common.ATTRS[cls].items():
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


class List(Convertible, list):

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
        return common.ATTRS[cls].get(cls.ALL)

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
