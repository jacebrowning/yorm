"""Package for YORM."""

import sys

__project__ = 'YORM'
__version__ = '0.5'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 3

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    from . import bases, converters
    from .utilities import UUID
    from .utilities import sync, sync_object, sync_instances, attr
    from .utilities import update, update_object, update_file
    from .bases import Container, Converter, Mappable, Convertible
except ImportError:  # pragma: no cover (manual test)
    pass
