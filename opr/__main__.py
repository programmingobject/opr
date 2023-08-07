# This file is placed in the Public Domain.
#
# pylint: disable=C0116,W0212


"main"


import os
import sys
import termios


from .command import Commands
from .console import CLI, Console
from .errored import Errors
from .message import Event
from .objects import Persist
from .runtime import Cfg, scan
from .threads import launch
from .utility import banner, parse, wait


from . import modules


def __dir__():
    return (
            'Cfg',
            'daemon',
            'main',
            'wrap',
            'wrapped'
           )


__all__ = __dir__()


Cfg.mod = "bsc,err,sts,thr"


Persist.workdir = os.path.expanduser(f"~/.{Cfg.name}")


def daemon():
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    os.umask(0)
    with open('/dev/null', 'r', encoding="utf-8") as sis:
        os.dup2(sis.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a+', encoding="utf-8") as sos:
        os.dup2(sos.fileno(), sys.stdout.fileno())
    with open('/dev/null', 'a+', encoding="utf-8") as ses:
        os.dup2(ses.fileno(), sys.stderr.fileno())


def wrap(func) -> None:
    old = termios.tcgetattr(sys.stdin.fileno())
    try:
        func()
    except (EOFError, KeyboardInterrupt):
        print("")
        sys.stdout.flush()
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
    Errors.wait()


def main():
    parse(Cfg, " ".join(sys.argv[1:]))
    if "v" in Cfg.opts:
        Errors.raw = print
        Errors.verbose = True
    if "d" in Cfg.opts:
        daemon()
        scan(modules, Cfg.mod, True)
        wait()
    elif "c" in Cfg.opts:
        print(banner(Cfg))
        csl = Console()
        scan(modules, Cfg.mod, True)
        csl.start()
        wait(Errors.wait)
    else:
        cli = CLI()
        scan(modules, Cfg.mod, False, True)
        evt = Event()
        evt.orig = repr(cli)
        evt.txt = Cfg.otxt
        evt._thr = launch(Commands.handle, evt)
        evt.wait()


def wrapped():
    wrap(main)


if __name__ == "__main__":
    wrapped()
