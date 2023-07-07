# This file is placed in the Public Domain.
#
# pylint: disable=E0001


"object programming runtime"


# IMPORTS


import io
import os
import readline
import sys
import termios
import threading
import time
import traceback


sys.path.insert(0, os.getcwd())


from opr.handler import Bus, Cfg, Commands, Errors, Event, Handler
from opr.handler import command, scanstr, waiter
from opr.loggers import Logging
from opr.objects import Default, Object, keys, kind, prt, update
from opr.parsers import parse
from opr.persist import Persist
from opr.threads import launch, name
from opr.utility import elapsed, spl


import opr.modules


# DEFINES


DATE = time.ctime(time.time()).replace("  ", " ")
NAME = sys.argv[0].split(os.sep)[-1]
STARTTIME = time.time()


Persist.workdir = os.path.expanduser(f"~/.{NAME}")


# CLASSES


class CLI(Handler):

    "command line interface"

    def announce(self, txt):
        "annouce text"

    def raw(self, txt):
        "print text"
        print(txt)


class Console(CLI):

    "cli in a loop"

    def handle(self, evt):
        "wait for events"
        CLI.handle(self, evt)
        evt.wait()

    def poll(self):
        "echo prompt"
        return self.event(input("> "))


# UTILITY


def banner():
    "print banner"
    print(f"{NAME.upper()} started {DATE}")
    sys.stdout.flush()


def daemon():
    "fork to the background"
    pid = os.fork()
    print(f"forking {pid}")
    if pid:
        os._exit(0)
    #os.setsid()
    os.umask(0)
    with open('/dev/null', 'r', encoding="utf-8") as sis:
        os.dup2(sis.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a+', encoding="utf-8") as sos:
        os.dup2(sos.fileno(), sys.stdout.fileno())
    with open('/dev/null', 'a+', encoding="utf-8") as ses:
        os.dup2(ses.fileno(), sys.stderr.fileno())


def wrap(func):
    "wrap function"
    fds = sys.stdin.fileno()
    gotterm = True
    try:
        old = termios.tcgetattr(fds)
    except termios.error:
        gotterm = False
    try:
        func()
    except (EOFError, KeyboardInterrupt):
        print("")
    finally:
        if gotterm:
            termios.tcsetattr(fds, termios.TCSADRAIN, old)
        waiter()


# COMMANDS


def cmd(event):
    "show list of commands"
    event.reply(','.join(sorted(keys(Commands.cmds))))


def err(event):
    "show errors"
    nmr = 0
    for exc in Errors.errors:
        stream = io.StringIO(
                             traceback.print_exception(
                                                       type(exc),
                                                       exc,
                                                       exc.__traceback__
                                                      )
                            )
        for line in stream.readlines():
            event.reply(line)
            nmr += 1
    if not nmr:
        event.reply("no error")


def flt(event):
    "show listeners"
    try:
        index = int(event.args[0])
        event.reply(prt(Bus.objs[index]))
        return
    except (KeyError, TypeError, IndexError, ValueError):
        pass
    event.reply(' | '.join([name(obj) for obj in Bus.objs]))


def mod(event):
    "show list of available modules"
    path = opr.modules.__path__[0]
    modlist = [x[:-3] for x in os.listdir(path) if x.endswith(".py") and x != "__init__.py"]
    mods = ",".join(sorted(modlist))
    event.reply(mods)


def rld(event):
    "reload"
    if not event.args:
        event.reply("rld <modname>")
        return
    modnames = event.args[0]
    for modname in spl(modnames):
        mods = getattr(opr.modules, modname)
        if not mods:
            event.reply(f"{modname} is not available")
            continue
        Commands.scan(mods)
        if "start" in dir(mods):
            thr = launch(mods.start)
        event.reply(f"reloaded {modname}")


def sts(event):
    "print status"
    nmr = 0
    for bot in Bus.objs:
        if 'state' in dir(bot):
            event.reply(prt(bot.state, skip='lastline'))
            nmr += 1
    if not nmr:
        event.reply("no status")


def thr(event):
    "show list of running threads"
    result = []
    for thread in sorted(threading.enumerate(), key=lambda x: x.name):
        if str(thread).startswith('<_'):
            continue
        obj = Object()
        update(obj, vars(thread))
        if getattr(obj, 'sleep', None):
            uptime = obj.sleep - int(time.time() - obj.state.latest)
        elif getattr(obj, 'starttime', None):
            uptime = int(time.time() - obj.starttime)
        else:
            uptime = int(time.time() - STARTTIME)
        result.append((uptime, thread.name))
    res = []
    for uptime, txt in sorted(result, key=lambda x: x[1]):
        lap = elapsed(uptime)
        res.append(f'{txt}/{lap}')
    if res:
        event.reply(' '.join(res))
    else:
        event.reply('no threads')


def unl(event):
    "unload"
    if not event.args:
        event.reply("unl <modname>")
        return
    modnames = event.args[0]
    for modname in spl(modnames):
        mods = getattr(opr.modules, modname)
        if mods:
            Commands.remove(mods)
            if "stop" in dir(mods):
                mods.stop()
        event.reply(f"unloaded {modname}")


def upt(event):
    "show uptime"
    event.reply(elapsed(time.time()-STARTTIME))


# RUNTIME


def main():
    "main program function"
    parse(Cfg, ' '.join(sys.argv[1:]))
    Commands.add(cmd)
    Commands.add(err)
    Commands.add(flt)
    Commands.add(mod)
    Commands.add(rld)
    Commands.add(sts)
    Commands.add(thr)
    Commands.add(unl)
    Commands.add(upt)
    if "v" in Cfg.opts and "d" not in Cfg.opts:
        Logging.verbose = True
        Logging.raw = print
    dowait = False
    scanstr(opr.modules, Cfg.mod)
    if Cfg.txt:
        cli = CLI()
        command(cli, Cfg.otxt)
    elif 'd' in Cfg.opts:
        daemon()
        dowait = True
    if "c" in Cfg.opts:
        dowait = True
    if dowait:
        banner()
        if 'c' in Cfg.opts and "d" not in Cfg.opts:
            csl = Console()
            csl.start()
        scanstr(opr.modules, Cfg.mod, True, wait=False)
        while 1:
            time.sleep(1.0)
            waiter()


if __name__ == "__main__":
    wrap(main)
