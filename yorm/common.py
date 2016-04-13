"""Shared internal classes and functions."""

import collections
import logging


# CONSTANTS ####################################################################

MAPPER = '__mapper__'
ALL = 'all'
UUID = 'UUID'

PRINT_VERBOSITY = 0  # minimum verbosity to using `print`
STR_VERBOSITY = 3  # minimum verbosity to use verbose `__str__`
MAX_VERBOSITY = 4  # maximum verbosity level implemented

OVERRIDE_MESSAGE = "Method must be implemented in subclasses"


# GLOBALS ######################################################################


verbosity = 0  # global verbosity setting for controlling string formatting

attrs = collections.defaultdict(collections.OrderedDict)


# LOGGING ######################################################################


def _trace(self, message, *args, **kwargs):  # pragma: no cover (manual test)
    """Handler for a new TRACE logging level."""
    if self.isEnabledFor(logging.DEBUG - 1):
        self._log(logging.DEBUG - 1, message, args, **kwargs)  # pylint: disable=protected-access


logging.addLevelName(logging.DEBUG - 1, "TRACE")
logging.Logger.trace = _trace


# DECORATORS ###################################################################


class classproperty(object):
    """Read-only class property decorator."""

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


# FUNCTIONS ####################################################################


def get_mapper(obj, *, expected=None):
    """Get the `Mapper` instance attached to an object."""
    try:
        mapper = object.__getattribute__(obj, MAPPER)
    except AttributeError:
        mapper = None

    if mapper and expected is False:
        msg = "{!r} is already mapped".format(obj)
        raise TypeError(msg)

    if not mapper and expected is True:
        msg = "{!r} is not mapped".format(obj)
        raise TypeError(msg)

    return mapper


def set_mapper(obj, mapper):
    """Attach a `Mapper` instance to an object."""
    setattr(obj, MAPPER, mapper)
    return mapper
