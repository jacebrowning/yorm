"""Base classes."""

import abc

from . import common

log = common.logger(__name__)


class Mappable(metaclass=abc.ABCMeta):  # pylint:disable=R0921

    """Base class for objects with attributes that map to YAML."""

    def __getattribute__(self, name):
        if name in ('yorm_mapper', 'yorm_attrs'):
            return object.__getattribute__(self, name)

        try:
            value = object.__getattribute__(self, name)
        except AttributeError:
            self.yorm_mapper.retrieve(self)
            value = object.__getattribute__(self, name)
        else:
            if name in self.yorm_attrs:
                self.yorm_mapper.retrieve(self)
                value = object.__getattribute__(self, name)

        return value

    def __setattr__(self, name, value):
        if hasattr(self, 'yorm_attrs') and name in self.yorm_attrs:
            converter = self.yorm_attrs[name]
            value = converter.to_value(value)

        object.__setattr__(self, name, value)

        if hasattr(self, 'yorm_attrs') and name in self.yorm_attrs:
            if hasattr(self, 'yorm_mapper') and self.yorm_mapper.auto:
                self.yorm_mapper.store(self)
            else:
                log.trace("automatic storage is off")

    def __enter__(self):
        log.debug("turning off automatic storage...")
        self.yorm_mapper.auto = False

    def __exit__(self, *_):
        log.debug("turning on automatic storage...")
        self.yorm_mapper.store(self)


class Converter(metaclass=abc.ABCMeta):  # pylint:disable=R0921

    """Base class for attribute converters."""

    TYPE = None  # type for inferred converters (set in subclasses)
    DEFAULT = None  # default value for conversion (set in subclasses)

    @abc.abstractclassmethod
    def to_value(cls, obj):  # pylint: disable=E0213
        """Convert the loaded value back to its original attribute type."""
        raise NotImplementedError("method must be implemented in subclasses")

    @abc.abstractclassmethod
    def to_data(cls, obj):  # pylint: disable=E0213
        """Convert the attribute's value for optimal dumping to YAML."""
        raise NotImplementedError("method must be implemented in subclasses")


class ContainerMeta(abc.ABCMeta):

    """Metaclass to initialize `yorm_attrs` on class declaration."""

    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        cls.yorm_attrs = {}


class Dictionary(metaclass=ContainerMeta):

    """Base class for a dictionary of attribute converters."""

    @classmethod
    def to_value(cls, obj):  # pylint: disable=E0213
        """Convert all loaded values back to its original attribute types."""
        if cls is Dictionary:
            msg = "Dictionary class must be subclassed to use"
            raise NotImplementedError(msg)

        value = {}

        yorm_attrs = cls.yorm_attrs.copy()

        for name, data in cls.to_dict(obj).items():
            try:
                converter = yorm_attrs.pop(name)
            except KeyError:
                from . import standard
                converter = standard.match(name, data, nested=True)
                cls.yorm_attrs[name] = converter
            value[name] = converter.to_value(data)

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


class List(metaclass=ContainerMeta):

    """Base class for a homogeneous list of attribute converters."""

    ALL = 'all'

    @common.classproperty
    def item_type(cls):  # pylint: disable=E0213
        """Get the converter class for all items."""
        return cls.yorm_attrs.get(cls.ALL)

    @classmethod
    def to_value(cls, obj):  # pylint: disable=E0213
        """Convert all loaded values back to the original attribute type."""
        if cls is List:
            raise NotImplementedError("List class must be subclassed to use")
        if not cls.item_type:
            raise NotImplementedError("List subclass must specify item type")

        value = []

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
