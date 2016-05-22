"""Package for YORM."""

import sys

__project__ = 'YORM'
__version__ = '1.0'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 3

if sys.version_info < PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    # pylint: disable=wrong-import-position
    from . import bases, types
    from .common import UUID
    from .decorators import sync, sync_object, sync_instances, attr
    from .utilities import create, find, match, load, save, delete
    from .bases import Container, Converter, Mappable, Convertible
except ImportError:  # pragma: no cover (manual test)
    pass
