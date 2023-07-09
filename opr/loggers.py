# This file is placed in the Public Domain.


"""logging"""

# IMPORTS


from opr.objects import doskip


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
