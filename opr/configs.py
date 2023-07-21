# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,E0402


"configurations"


from .objects import Object


def __dir__():
    return (
            "Cfg",
           )


__all__ = __dir__()


Cfg = Object()
