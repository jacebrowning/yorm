"""Package for YORM."""

import sys

__project__ = 'YORM'
__version__ = '0.4.1rc7'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 3

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    from . import base, converters
    from .utilities import UUID
    from .utilities import sync, sync_object, sync_instances, attr
    from .utilities import update, update_object, update_file
    from .base.mappable import Mappable
    from .base.convertible import Converter, Convertible
except ImportError:  # pragma: no cover (manual test)
    pass
