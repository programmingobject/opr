# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"logging"


from .utility import skip


def __dir__():
    return (
            'Logging',
           )


__all__ = __dir__()


class Logging:

    skip = 'PING,PONG,PRIVMSG'
    verbose = False

    @staticmethod
    def debug(txt) -> None:
        if Logging.verbose and not skip(txt, Logging.skip):
            Logging.raw(txt)

    @staticmethod
    def raw(txt) -> None:
        pass
