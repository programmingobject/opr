# This file is placed in the Public Domain.


"""logging"""


__author__ = "Bart Thate <programmingobject@gmail.com>"


# INTERFACE


def __dir__():
    return (
            'Logging',
           )


__all__ = __dir__()


# CLASSES


class Logging:

    """stub to echo to stdout"""

    skip = 'PING,PONG,PRIVMSG'
    verbose = False

    @staticmethod
    def debug(txt) -> None:
        """check for verbose"""
        if Logging.verbose and not doskip(txt, Logging.skip):
            Logging.raw(txt)

    @staticmethod
    def raw(txt) -> None:
        """override this with print"""


# UTILITY


def doskip(txt, skipping) -> bool:
    """check if text needs to be skipped"""
    for skip in dosplit(skipping):
        if skip in txt:
            return True
    return False


def dosplit(txt) -> []:
    """split comma seperated string"""
    try:
        result = txt.split(',')
    except (TypeError, ValueError):
        result = txt
    return [x for x in result if x]
