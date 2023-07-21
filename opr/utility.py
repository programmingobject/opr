# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"utilities"


import os
import pathlib
import time
import types


def __dir__():
    return (
            "banner",
            "cdir",
            "laps",
            "name",
            "skip",
            "spl",
            "strip",
            "wait"
           )


__all__ = __dir__()


def banner(names, version):
    times = time.ctime(time.time())
    return f"{names.upper()} {version} {times}"


def cdir(pth) -> None:
    if not pth.endswith(os.sep):
        pth = os.path.dirname(pth)
    pth = pathlib.Path(pth)
    os.makedirs(pth, exist_ok=True)


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
    if years and short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def name(obj) -> str:
    typ = type(obj)
    if isinstance(typ, types.ModuleType):
        return obj.__name__
    if '__self__' in dir(obj):
        clz = obj.__self__.__class__.__name__
        nme = obj.__name__
        return f'{clz}.{nme}'
    if '__class__' in dir(obj) and '__name__' in dir(obj):
        clz = obj.__class__.__name__
        nme = obj.__name__
        return f'{clz}.{nme}'
    if '__class__' in dir(obj):
        return obj.__class__.__name__
    if '__name__' in dir(obj):
        clz = obj.__class__.__name__
        nme = obj.__name__
        return f'{clz}.{nme}'
    return None


def skip(txt, skipping) -> bool:
    for skp in spl(skipping):
        if skp in txt:
            return True
    return False


def spl(txt) -> []:
    try:
        res = txt.split(',')
    except (TypeError, ValueError):
        res = txt
    return [x for x in res if x]


def strip(path) -> str:
    return os.sep.join(path.split(os.sep)[-4:])


def wait():
    while 1:
        time.sleep(1.0)
