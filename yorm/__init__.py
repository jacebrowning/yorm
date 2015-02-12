"""Package for YORM."""

import sys

__project__ = 'YORM'
__version__ = '0.2.1'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 3

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    from . import standard, extended, container
    from .utilities import UUID, store, store_instances, map_attr
    from .base import Mappable, Converter
except ImportError:  # pragma: no cover (manual test)
    pass
