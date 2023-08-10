# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0718


"commands"


import inspect


from .listens import Bus
from .errored import Errors
from .objfunc import parse


def __dir__():
    return (
            'Commands',
           )


__all__ = __dir__()


class Commands:

    cmds = {}
    errors = []

    @staticmethod
    def add(func):
        Commands.cmds[func.__name__] = func

    @staticmethod
    def handle(evt):
        if "txt" in dir(evt):
            parse(evt, evt.txt)
            func = Commands.cmds.get(evt.cmd, None)
            if func:
                try:
                    func(evt)
                    Bus.show(evt)
                except Exception as ex:
                    exc = ex.with_traceback(ex.__traceback__)
                    Errors.errors.append(exc)
        evt.ready()

    @staticmethod
    def remove(name):
        try:
            del Commands.cmds[name]
        except KeyError:
            pass

    @staticmethod
    def scan(mod) -> None:
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmd.__code__.co_varnames:
                Commands.add(cmd)
