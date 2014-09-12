"""Functions and decorators."""

import uuid

UUID = 'UUID'


def store(instance, path, mapping=None):
    """Enable YAML mapping on an object.

    :param instance: object to patch with YAML mapping behavior
    :param path: file path for dump/load
    :param mapping: dictionary of attribute names mapped to converter classes

    """
    mapping = mapping or {}
    # TODO: monkey patch base class
    instance.yorm_path = path
    instance.yorm_attrs = mapping
    return instance


def store_instances(path_format, format_spec=None, mapping=None):
    """Class decorator to enable YAML mapping after instantiation.

    :param path_format: formatting string to create file paths for dump/load
    :param format_spec: dictionary to use for string formatting
    :param mapping: dictionary of attribute names mapped to converter classes

    """
    format_spec = format_spec or {}
    mapping = mapping or {}

    def decorator(cls):
        """Class decorator."""
        if hasattr(cls, 'yorm_attrs'):
            cls.yorm_attrs.update(mapping)
        else:
            cls.yorm_attrs = mapping

        class Decorated(cls):

            """Decorated class."""

            def __init__(self, *_args, **_kwargs):
                super().__init__(*_args, **_kwargs)
                if '{' + UUID + '}' in path_format:
                    format_spec[UUID] = uuid.uuid4().hex
                self.yorm_path = path_format.format(**format_spec)

        return Decorated

    return decorator


def map_attr(**kwargs):
    """Class decorator to map attributes to converters.

    :param kwargs: keyword arguments mapping attribute name to converter class

    """
    def decorator(cls):
        """Class decorator."""
        if not hasattr(cls, 'yorm_attrs'):
            cls.yorm_attrs = {}
        for name, converter in kwargs.items():
            cls.yorm_attrs[name] = converter
        return cls

    return decorator
