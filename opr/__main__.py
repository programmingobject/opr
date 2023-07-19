# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"object programming runtime"


__author__ = "Bart Thate <programmingobject@gmail.com>"


import os
import readline
import sys
import termios
import _thread


sys.path.insert(0, os.getcwd())


from opr import Cfg


Cfg.mod = "bsc"
Cfg.name = "opr"
Cfg.verbose = False
Cfg.version = 241


from opr import Broker, Command, Event, Logging, Persist, Reactor
from opr import banner, parse, scan, waiter
from opr import modules


Persist.workdir = os.path.expanduser(f"~/.{Cfg.name}")


readline.redisplay()


class CLI(Reactor):

    def __init__(self):
        Reactor.__init__(self)
        Broker.add(self)
        self.register("event", Command.handle)

    def announce(self, txt):
        pass

    def raw(self, txt):
        print(txt)


class Console(CLI):

    def __init__(self):
        CLI.__init__(self)

    def handle(self, evt):
        Command.handle(evt)
        evt.wait()

    def poll(self):
        try:
            return self.event(input("> "))
        except EOFError:
            _thread.interrupt_main()

def cprint(txt):
    print(txt)
    sys.stdout.flush()


def wrap(func) -> None:
    old = termios.tcgetattr(sys.stdin.fileno())
    try:
        func()
    except (EOFError, KeyboardInterrupt):
        print("")
        sys.stdout.flush()
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
        waiter()


def main():
    parse(Cfg, " ".join(sys.argv[1:]))
    if "v" in Cfg.opts:
        Logging.raw = print
        Logging.verbose = True
    if "c" in Cfg.opts:
        print(banner(Cfg.name, Cfg.version))
        csl = Console()
        scan(modules, Cfg.mod, True, "a" in Cfg.opts)
        csl.loop()
    else:
        cli = CLI()
        scan(modules, Cfg.mod, False, True)
        evt = Event()
        evt.orig = repr(cli)
        evt.txt = Cfg.otxt
        Command.handle(evt)


if __name__ == "__main__":
    wrap(main)
    waiter()
