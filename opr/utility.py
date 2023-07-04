# This file is placed in the Public Domain.


"utility"


# IMPORTS


import os
import pathlib


# DEFINES


def __dir__():
    return (
            'cdir',
            'doskip',
            'elapsed',
            'fnclass',
            'fntime',
            'spl',
            'strip',
            'touch'
           )


# UTILITY


def cdir(pth) -> None:
    "Create directory"
    if not pth.endswith(os.sep):
        pth = os.path.dirname(pth)
    pth = pathlib.Path(pth)
    os.makedirs(pth, exist_ok=True)


def doskip(txt, skipping) -> bool:
    "check if text needs to be skipped"
    for skip in spl(skipping):
        if skip in txt:
            return True
    return False


def elapsed(seconds, short=True) -> str:
    "return elapsed time string"
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


def spl(txt) -> []:
    "split comma seperated string" 
    try:
        res = txt.split(',')
    except (TypeError, ValueError):
        res = txt
    return [x for x in res if x]


def strip(pth) -> str:
    "strip path to ident part"
    return os.sep.join(pth.split(os.sep)[-4:])


def touch(fname) -> None:
    "touch a file"
    fds = os.open(fname, os.O_WRONLY | os.O_CREAT)
    os.close(fds)
