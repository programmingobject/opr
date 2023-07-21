# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"error handling"


import io
import traceback


from .loggers import Logging
from .objects import Object


def __dir__():
    return (
            'Error',
            'Errors',
            'waiter'
           )


__all__ = __dir__()


class Error(Exception):

    pass


class Errors(Object):

    errors = []

    @staticmethod
    def handle(ex) -> None:
        exc = ex.with_traceback(ex.__traceback__)
        Errors.errors.append(exc)

    @staticmethod
    def size():
        return len(Errors.errors)


def waiter(clear=True):
    got = []
    for ex in Errors.errors:
        stream = io.StringIO(
                             traceback.print_exception(
                                                       type(ex),
                                                       ex,
                                                       ex.__traceback__
                                                      )
                            )
        for line in stream.readlines():
            Logging.debug(line)
        got.append(ex)
    if clear:
        for exc in got:
            Errors.errors.remove(exc)
