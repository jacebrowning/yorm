"""Converter classes for abstract container types."""

from .. import common
from ..base.container import Container
from . import standard

log = common.logger(__name__)


class Dictionary(Container, dict):

    """Base class for a dictionary of attribute converters."""

    def apply(self, data):
        value = self.to_value(data)
        self.clear()
        self.update(value)

    @classmethod
    def to_value(cls, data):
        value = cls.default()

        # Convert object attributes to a dictionary
        attrs = common.ATTRS[cls].copy()
        if isinstance(data, cls):
            items = data.__dict__.items()
            dictionary = {k: v for k, v in items if k in attrs}
        else:
            dictionary = cls.to_dict(data)

        # Map object attributes to converters
        for name, data in dictionary.items():
            try:
                converter = attrs.pop(name)
            except KeyError:
                converter = standard.match(name, data, nested=True)
                common.ATTRS[cls][name] = converter

            # Convert the loaded data
            if issubclass(converter, Container):
                container = converter()
                container.apply(data)
                value[name] = container
            else:
                value[name] = converter.to_value(data)

        # Create default values for unmapped converters
        for name, converter in attrs.items():
            if issubclass(converter, Container):
                value[name] = converter()
            else:
                value[name] = converter.to_value(None)
            log.warn("added missing nested key '%s'...", name)

        return value

    @classmethod
    def default(cls):
        """Create an uninitialized object."""
        if cls is Dictionary:
            msg = "Dictionary class must be subclassed to use"
            raise NotImplementedError(msg)

        return dict()

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

    @classmethod
    def to_data(cls, value):
        value = cls.to_value(value)

        data = {}

        for name, converter in common.ATTRS[cls].items():
            data[name] = converter.to_data(value.get(name, None))

        return data


class List(Container, list):

    """Base class for a homogeneous list of attribute converters."""

    ALL = 'all'

    def apply(self, data):
        value = self.to_value(data)
        self[:] = value[:]

    @classmethod
    def to_value(cls, data):
        value = cls.default()

        for item in cls.to_list(data):
            if issubclass(cls.item_type, Container):
                container = cls.item_type()  # pylint: disable=E1120
                container.apply(item)
                value.append(container)
            else:
                value.append(cls.item_type.to_value(item))

        return value

    @classmethod
    def default(cls):
        """Create an uninitialized object."""
        if cls is List:
            raise NotImplementedError("List class must be subclassed to use")
        if not cls.item_type:
            raise NotImplementedError("List subclass must specify item type")

        return cls.__new__(cls)

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

    @common.classproperty
    def item_type(cls):  # pylint: disable=E0213
        """Get the converter class for all items."""
        return common.ATTRS[cls].get(cls.ALL)

    @classmethod
    def to_data(cls, value):
        value = cls.to_value(value)

        data = []

        if value:
            for item in value:
                data.append(cls.item_type.to_data(item))

        return data
