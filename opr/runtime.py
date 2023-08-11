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
from .utility import listmods


def __dir__():
    return (
            "Cfg",
            'scan'
           )


__all__ = __dir__()


STARTTIME = time.time()


Cfg = Default()
Cfg.name = __file__.split(os.sep)[-2]


def scan(pkg, modstr, initer=False, doall=False, wait=False) -> None:
    path = pkg.__path__[0]
    inited = []
    scanned = []
    threads = []
    for modname in listmods(path):
        if not doall and modname not in modstr:
            continue
        module = getattr(pkg, modname, None)
        if not module:
            continue
        scanned.append(modname)
        Commands.scan(module)
        Storage.scan(module)
        if initer and "init" in dir(module):
            inited.append(modname)
            threads.append(launch(module.init, name=f"init {modname}"))
    if wait:
        for thread in threads:
            thread.join()
    Errors.debug(f"scanned {','.join(scanned)}")
    Errors.debug(f"init {','.join(inited)}")
    return threads
