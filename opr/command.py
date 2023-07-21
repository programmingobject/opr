# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0718,E0402


"commands"


import inspect
import os


from .errored import Errors
from .objects import Object, get
from .parsers import parse
from .threads import launch
from .utility import spl


def __dir__():
    return (
            'Command',
            'scan'
           )


__all__ = __dir__()


class Command(Object):

    cmds = Object()

    @staticmethod
    def add(func):
        Command.cmds[func.__name__] = func

    @staticmethod
    def handle(evt):
        if "txt" in evt:
            parse(evt, evt.txt)
            func = get(Command.cmds, evt.cmd, None)
            if func:
                try:
                    func(evt)
                    evt.show()
                except Exception as ex:
                    exc = ex.with_traceback(ex.__traceback__)
                    Errors.errors.append(exc)
        evt.ready()

    @staticmethod
    def remove(name):
        try:
            del Command.cmds[name]
        except KeyError:
            pass

    @staticmethod
    def scan(mod) -> None:
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmd.__code__.co_varnames:
                Command.add(cmd)


def scan(pkg, mods, init=None, doall=False, wait=False) -> None:
    path = pkg.__path__[0]
    if doall:
        modlist = [
                   x[:-3] for x in os.listdir(path)
                   if x.endswith(".py")
                   and x not in ["__init__.py", "__main__.py"]
                  ]
        mods = ",".join(sorted(modlist))
    threads = []
    for modname in spl(mods):
        module = getattr(pkg, modname, None)
        if module:
            Command.scan(module)
        if init and "start" in dir(module):
            threads.append(launch(module.start))
    if wait and threads:
        for thr in threads:
            thr.join()
