#!/usr/bin/env python

"""Package for YORM."""

__project__ = 'YORM'
__version__ = '0.0.0'

VERSION = __project__ + '-' + __version__

try:
    from .utilities import yormalize, yattr
    from .base import Yattribute
except ImportError:  # pragma: no cover (manual test)
    pass
