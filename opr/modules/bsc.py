# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0401


"basic commands"


import io
import os
import threading
import time
import traceback


from .. import Broker, Command, Errors, Object
from .. import laps, prt, spl, update


from ..threads import name


STARTTIME = time.time()


def __dir__():
    return (
            "cmd",
            "err",
            "flt",
            'mod',
            "rld",
            "thr",
            "unl"
           )


__all__ = __dir__()


def cmd(event):
    event.reply(",".join(sorted(Command.cmds)))


def err(event):
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
    try:
        index = int(event.args[0])
        event.reply(prt(Broker.objs[index]))
        return
    except (KeyError, TypeError, IndexError, ValueError):
        pass
    event.reply(' | '.join([name(obj) for obj in Broker.objs]))


def mod(event):
    from .. import modules
    path = modules.__path__[0]
    modlist = [
               x[:-3] for x in os.listdir(path)
               if x.endswith(".py")
               and x not in ["__main__.py", "__init__.py"]
              ]
    mods = ",".join(sorted(modlist))
    event.reply(mods)


def rld(event):
    if not event.args:
        event.reply("rld <modname>")
        return
    from .. import modules
    modnames = event.args[0]
    for modname in spl(modnames):
        mods = getattr(modules, modname, None)
        if not mods:
            event.reply(f"{modname} is not available")
            continue
        Command.scan(mods)
        if "start" in dir(mods):
            mods.start()
        event.reply(f"reloaded {modname}")


def sts(event):
    nmr = 0
    for bot in Broker.objs:
        if 'state' in dir(bot):
            event.reply(prt(bot.state, skip='lastline'))
            nmr += 1
    if not nmr:
        event.reply("no status")


def thr(event):
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
        lap = laps(uptime)
        res.append(f'{txt}/{lap}')
    if res:
        event.reply(' '.join(res))
    else:
        event.reply('no threads')


def unl(event):
    if not event.args:
        event.reply("unl <modname>")
        return
    from .. import modules
    modnames = event.args[0]
    for modname in spl(modnames):
        mods = getattr(modules, modname, None)
        if mods:
            Command.remove(mods)
            if "stop" in dir(mods):
                mods.stop()
        event.reply(f"unloaded {modname}")
