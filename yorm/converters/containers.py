"""Converter classes for builtin container types."""

from .. import common
from ..base.convertible import Convertible
from . import standard

log = common.logger(__name__)


class Dictionary(Convertible, dict):

    """Base class for a dictionary of attribute converters."""

    def __new__(cls, *args, **kwargs):
        if cls is Dictionary:
            msg = "Dictionary class must be subclassed to use"
            raise NotImplementedError(msg)
        return super().__new__(cls, *args, **kwargs)

    @classmethod
    def create_default(cls):
        """Create an uninitialized object."""
        if cls is Dictionary:
            msg = "Dictionary class must be subclassed to use"
            raise NotImplementedError(msg)
        return cls.__new__(cls)

    @classmethod
    def to_data(cls, value):
        value = cls.to_value(value)

        data = {}

        for name, converter in common.ATTRS[cls].items():
            data[name] = converter.to_data(value.get(name, None))

        return data

    def update_value(self, data):
        # TODO: replace to_value and to_data
        cls = self.__class__

        # Convert object attributes to a dictionary
        attrs = common.ATTRS[cls].copy()
        if isinstance(data, cls):
            dictionary = {}
            for k, v in data.items():
                if k in attrs:
                    dictionary[k] = v
            for k, v in data.__dict__.items():
                if k in attrs:
                    dictionary[k] = v
        else:
            dictionary = to_dict(data)

        # Map object attributes to converters
        for name, data in dictionary.items():
            try:
                converter = attrs.pop(name)
            except KeyError:
                converter = standard.match(name, data, nested=True)
                common.ATTRS[cls][name] = converter

            # Convert the loaded data
            try:

                attr = self[name]
            except KeyError:
                attr = converter.create_default()


            if isinstance(attr, converter) and issubclass(converter, Convertible):
                attr.update_value(data)
            else:
                attr = converter.to_value(data)
                self[name] = attr




        # Create default values for unmapped converters
        for name, converter in attrs.items():
            self[name] = converter.create_default()
            log.warn("added missing nested key '%s'...", name)



class List(Convertible, list):

    """Base class for a homogeneous list of attribute converters."""

    ALL = 'all'

    def __new__(cls, *args, **kwargs):
        if cls is List:
            raise NotImplementedError("List class must be subclassed to use")
        if not cls.item_type:
            raise NotImplementedError("List subclass must specify item type")
        return super().__new__(cls, *args, **kwargs)

    @common.classproperty
    def item_type(cls):  # pylint: disable=E0213
        """Get the converter class for all items."""
        return common.ATTRS[cls].get(cls.ALL)

    @classmethod
    def create_default(cls):
        """Create an uninitialized object."""
        return cls.__new__(cls)

    @classmethod
    def to_data(cls, value):
        value = cls.to_value(value)

        data = []

        if value:
            for item in value:
                data.append(cls.item_type.to_data(item))

        return data

    def update_value(self, data):
        # TODO: replace to_value and to_data
        cls = self.__class__

        # TODO: is `default` still needed?
        value = cls.create_default()

        converter = cls.item_type

        for item in to_list(data):

            try:
                attr = self[len(value)]
            except IndexError:
                attr = converter.create_default()


            if isinstance(attr, converter) and issubclass(converter, Convertible):
                attr.update_value(item)
            else:
                attr = converter.to_value(item)


            value.append(attr)

        self[:] = value[:]


def to_dict(obj):
    """Convert a dictionary-like object to a dictionary.

    >>> to_dict({'key': 42})
    {'key': 42}

    >>> to_dict("key=42")
    {'key': '42'}

    >>> to_dict("key")
    {'key': None}

    >>> to_dict(None)
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


def to_list(obj):
    """Convert a list-like object to a list.

    >>> to_list([1, 2, 3])
    [1, 2, 3]

    >>> to_list("a,b,c")
    ['a', 'b', 'c']

    >>> to_list("item")
    ['item']

    >>> to_list(None)
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
