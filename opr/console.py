# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,R1710


"console"


import sys
import threading
import _thread


from .command import Commands
from .listens import Bus
from .reactor import Reactor


def __dir__():
    return (
            'CLI',
            'Console'
           )


__all__ = __dir__()


class CLI(Reactor):

    def __init__(self):
        Reactor.__init__(self)
        self.register("command", Commands.handle)
        Bus.add(self)

    def announce(self, txt):
        pass

    def raw(self, txt):
        print(txt)


class Console(CLI):

    prompting = threading.Event()

    def announce(self, txt):
        self.raw(txt)

    def handle(self, evt):
        Commands.handle(evt)
        evt.wait()

    def prompt(self):
        self.prompting.set()
        inp = input("> ")
        self.prompting.clear()
        return inp

    def poll(self):
        try:
            return self.event(self.prompt())
        except EOFError:
            _thread.interrupt_main()

    def raw(self, txt):
        if Console.prompting.is_set():
            txt = "\n" + txt
        print(txt)
        Console.prompting.clear()
        sys.stdout.flush()
