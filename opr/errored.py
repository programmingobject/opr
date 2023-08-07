# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116


"reactor"


import io
import traceback


from .utility import doskip


def __dir__():
    return (
            'Errors',
           )


__all__ = __dir__()


class Errors:

    skip = 'PING,PONG,PRIVMSG'
    verbose = False
    errors = []

    @staticmethod
    def debug(txt) -> None:
        if Errors.verbose and not doskip(txt, Errors.skip):
            Errors.raw(txt)

    @staticmethod
    def handle(exc):
        excp = exc.with_traceback(exc.__traceback__)
        Errors.errors.append(excp)

    @staticmethod
    def raw(txt) -> None:
        pass

    @staticmethod
    def wait():
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
                Errors.debug(line)
            got.append(ex)
        for exc in got:
            if exc in Errors.errors:
                Errors.errors.remove(exc)
