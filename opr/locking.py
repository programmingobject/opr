# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903


"locking space"


import _thread


disklock = _thread.allocate_lock()
hooklock = _thread.allocate_lock()

