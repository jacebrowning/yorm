"""Converter classes for builtin container types."""

from .. import common
from ..bases import Convertible, Container
from . import standard

log = common.logger(__name__)


class Dictionary(Convertible, Container, dict):

    """Base class for a dictionary of attribute converters."""

    def __new__(cls, *args, **kwargs):
        if cls is Dictionary:
            msg = "Dictionary class must be subclassed to use"
            raise NotImplementedError(msg)
        return super().__new__(cls, *args, **kwargs)

    @classmethod
    def to_data(cls, value):
        value2 = cls.create_default()
        value2.update_value(value, match=None)

        data = {}

        for name, converter in common.attrs[cls].items():
            data[name] = converter.to_data(value2.get(name, None))

        return data

    def update_value(self, data, match=standard.match):
        cls = self.__class__
        value = cls.create_default()

        # Convert object attributes to a dictionary
        attrs = common.attrs[cls].copy()
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
        for name, data2 in dictionary.items():

            try:
                converter = attrs.pop(name)
            except KeyError:
                if match:
                    converter = match(name, data2, nested=True)
                    common.attrs[cls][name] = converter
                else:
                    continue

            try:
                attr = self[name]
            except KeyError:
                attr = converter.create_default()

            if all((isinstance(attr, converter),
                    issubclass(converter, Convertible))):
                attr.update_value(data2, match=match)
            else:
                attr = converter.to_value(data2)

            value[name] = attr

        # Create default values for unmapped converters
        for name, converter in attrs.items():
            value[name] = converter.create_default()
            # TODO: clean this up more
            # https://github.com/jacebrowning/yorm/issues/69
            log.info("added missing nested key '%s'...", name)

        # Apply the new value
        self.clear()
        self.update(value)


class List(Convertible, Container, list):

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
        return common.attrs[cls].get(cls.ALL)

    @classmethod
    def to_data(cls, value):
        value2 = cls.create_default()
        value2.update_value(value, match=None)

        data = []

        if value2:
            for item in value2:
                data.append(cls.item_type.to_data(item))

        return data

    def update_value(self, data, match=standard.match):
        cls = self.__class__
        value = cls.create_default()

        # Get the converter for all items
        converter = cls.item_type

        # Convert the loaded data
        for item in to_list(data):

            try:
                attr = self[len(value)]
            except IndexError:
                attr = converter.create_default()

            if all((isinstance(attr, converter),
                    issubclass(converter, Convertible))):
                attr.update_value(item, match=match)
            else:
                attr = converter.to_value(item)

            value.append(attr)

        # Apply the new value
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
        try:
            return obj.__dict__
        except AttributeError:
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
