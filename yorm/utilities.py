"""Functions and decorators."""

import uuid

UUID = 'UUID'


def store(instance, path, mapping):
    """Enable YAML mapping on an object.

    :param instance: object to patch with YAML mapping behavior
    :param path: file path for dump/load
    :param mapping: dictionary of attribute names mapped to converter classes

    """
    # TODO: monkey patch base class
    instance.__path__ = path
    return instance


def store_instances(path_format, format_spec=None, mapping=None):
    """Class decorator to enable YAML mapping after instantiation.

    :param path_format: formatting string to create file paths for dump/load
    :param format_spec: dictionary to use for string formatting
    :param mapping: dictionary of attribute names mapped to converter classes

    """
    format_spec = format_spec or {}

    def decorator(cls):
        """Class decorator."""
        class Decorated(cls):

            """Decorated class."""

            def __init__(self, *_args, **_kwargs):
                super().__init__(*_args, **_kwargs)
                if '{' + UUID + '}' in path_format:
                    format_spec[UUID] = uuid.uuid4()
                self.__path__ = path_format.format(**format_spec)

        return Decorated

    return decorator


def map_attr(**kwargs):
    """Class decorator to map attributes to converters.

    :param kwargs: keyword arguments mapping attribute name to converter class

    """
    def decorator(cls):
        """Class decorator."""
        return cls

    return decorator
