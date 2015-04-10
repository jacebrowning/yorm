"""Base class for mapped objects."""

import abc

from .. import common

log = common.logger(__name__)


MAPPER = 'yorm_mapper'


class Mappable(metaclass=abc.ABCMeta):

    """Base class for objects with attributes mapped to file."""

    def __getattribute__(self, name):
        if name == MAPPER:
            return object.__getattribute__(self, name)

        mapper = getattr(self, MAPPER, None)

        try:
            value = object.__getattribute__(self, name)
        except AttributeError as exc:
            if mapper:
                mapper.fetch()
                value = object.__getattribute__(self, name)
            else:
                raise exc from None
        else:
            if mapper and name in mapper.attrs:
                mapper.fetch()
                value = object.__getattribute__(self, name)

        return value

    def __setattr__(self, name, value):
        mapper = getattr(self, MAPPER, None)

        if mapper and name in mapper.attrs:
            converter = mapper.attrs[name]
            value = converter.to_value(value)

        object.__setattr__(self, name, value)

        if mapper:
            log.critical(mapper.attrs)

        if mapper and name in mapper.attrs:
            if mapper.auto:
                self.yorm_mapper.store()
            else:
                log.trace("automatic storage is off")

    def __enter__(self):
        log.debug("turning off automatic storage...")
        mapper = getattr(self, MAPPER)
        mapper.auto = False

    def __exit__(self, *_):
        log.debug("turning on automatic storage...")
        mapper = getattr(self, MAPPER)
        mapper.store()
