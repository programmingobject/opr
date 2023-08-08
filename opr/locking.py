# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903


"locking space"


import _thread


def __dir__():
    return (
            'disklock',
            'hooklock',
            'jsonlock'
           )


__all__ = __dir__()


disklock = _thread.allocate_lock()
hooklock = _thread.allocate_lock()
jsonlock = _thread.allocate_lock()
