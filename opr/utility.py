# This file is placed in the Public Domain.
#
# pylint: disable=C0116,W0212


"utilities"


import os
import pathlib
import time
import types


def __dir__():
    return (
            'banner',
            'cdir',
            'doskip',
            'listmods',
            'name',
            'nme',
            'spl',
            'strip',
            'tme',
            'wait'
           )


__all__ = __dir__()


def banner(cfg):
    if cfg.mod:
        mods = cfg.mod.upper()
    else:
        mods = "CONSOLE"
    return f"{cfg.name.upper()} started {tme()} {mods} {cfg.opts.upper()}"


def cdir(pth) -> None:
    if not pth.endswith(os.sep):
        pth = os.path.dirname(pth)
    pth = pathlib.Path(pth)
    os.makedirs(pth, exist_ok=True)


def doskip(txt, skipping) -> bool:
    for skp in spl(skipping):
        if skp in txt:
            return True
    return False


def fnclass(fnm):
    return fnm.split(os.sep)[-4]


def fntime(daystr) -> float:
    daystr = daystr.replace('_', ':')
    datestr = ' '.join(daystr.split(os.sep)[-2:])
    if '.' in datestr:
        datestr, rest = datestr.rsplit('.', 1)
    else:
        rest = ''
    timed = time.mktime(time.strptime(datestr, '%Y-%m-%d %H:%M:%S'))
    if rest:
        timed += float('.' + rest)
    else:
        timed = 0
    return timed


def laps(seconds, short=True) -> str:
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    year = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    nsec -= int(minute*minutes)
    sec = int(nsec)
    if years:
        txt += f"{years}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if nrdays and short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def listmods(path):
    return [
            x[:-3].strip() for x in os.listdir(path)
            if x.endswith(".py")
            and x not in ["__init__.py", "__main__.py"]
           ]


def name(obj) -> str:
    typ = type(obj)
    if isinstance(typ, types.ModuleType):
        return obj.__name__
    if '__self__' in dir(obj):
        return f'{obj.__self__.__class__.__name__}.{obj.__name__}'
    if '__class__' in dir(obj) and '__name__' in dir(obj):
        return f'{obj.__class__.__name__}.{obj.__name__}'
    if '__class__' in dir(obj):
        return f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    if '__name__' in dir(obj):
        return f'{obj.__class__.__name__}.{obj.__name__}'
    return None


def nme():
    return __file__.split(os.sep)[-2]


def spl(txt) -> []:
    try:
        res = txt.split(',')
    except (TypeError, ValueError):
        res = txt
    return [x for x in res if x]


def strip(path) -> str:
    return os.sep.join(path.split(os.sep)[-4:])


def tme():
    return " ".join(time.ctime(time.time()).split()[1:])


def wait(func=None):
    while 1:
        time.sleep(1.0)
        if func:
            func()
