# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"logging"


__author__ = "Bart Thate <programmingobject@gmail.com>"


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
        if Logging.verbose and not doskip(txt, Logging.skip):
            Logging.raw(txt)

    @staticmethod
    def raw(txt) -> None:
        pass


# UTILITY


def doskip(txt, skipping) -> bool:
    for skip in dosplit(skipping):
        if skip in txt:
            return True
    return False


def dosplit(txt) -> []:
    try:
        result = txt.split(',')
    except (TypeError, ValueError):
        result = txt
    return [x for x in result if x]
