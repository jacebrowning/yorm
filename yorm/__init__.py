#!/usr/bin/env python

"""Package for YORM."""

__project__ = 'YORM'
__version__ = '0.2'

VERSION = __project__ + '-' + __version__

try:
    from . import standard, extended, container
    from .utilities import UUID, store, store_instances, map_attr
    from .base import Mappable, Converter
except ImportError:  # pragma: no cover (manual test)
    pass
