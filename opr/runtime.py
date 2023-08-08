# This file is placed in the Public Domain.
#
# pylint: disable=C0116


"runtime"


import os
import time


from .command import Commands
from .default import Default
from .errored import Errors
from .storage import Storage
from .threads import launch
from .utility import listmods, spl


def __dir__():
    return (
            "Cfg",
            'init',
            'scan'
           )


__all__ = __dir__()


STARTTIME = time.time()


Cfg = Default()
Cfg.name = __file__.split(os.sep)[-2]


def init(pkg, modstr):
    res = []
    for modname in spl(modstr):
        mod = getattr(pkg, modname, None)
        if mod and "init" in dir(mod):
            Errors.debug(f"init {modname}")
            res.append(launch(mod.init))
    return res


def scan(pkg, modstr, initer=None, doall=False) -> None:
    path = pkg.__path__[0]
    threads = []
    for modname in listmods(path):
        if not doall and modname not in modstr:
            continue
        module = getattr(pkg, modname, None)
        if not module:
            continue
        Errors.debug(f"scan {modname}")
        Commands.scan(module)
        Storage.scan(module)
        if initer and "init" in dir(module):
            Errors.debug(f"init {modname}")
            threads.append(launch(module.init, name=f"init {modname}"))
    return threads
