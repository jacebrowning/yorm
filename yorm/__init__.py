"""Package for YORM."""

import sys

__project__ = 'YORM'
__version__ = '0.3a1'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 3

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    from . import standard, extended, container
    from .utilities import UUID
    from .utilities import sync, sync_object, sync_instances, attr
    from .utilities import update, update_object, update_file
    from .base import Mappable, Converter
except ImportError:  # pragma: no cover (manual test)
    pass
