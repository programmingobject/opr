# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"module with the locks"


__author__ = "Bart Thate <skullbonesandnumber@gmail.com>"


import _thread


def __dir__():
    return (
            'disklock',
            'saylock'
           )


__all__ = __dir__()


disklock = _thread.allocate_lock()
saylock = _thread.allocate_lock()
