# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"persistence"


import os
import sys
import time


from .objects import kind
from .decoder import load
from .encoder import dump
from .locking import disklock
from .objects import Object, ident, items, update
from .utility import cdir, strip


def __dir__():
    return (
            'Persist',
            'find',
            'last',
            'read',
            'search',
            'write'
           )


__all__ = __dir__()


class Persist:

    workdir = ""

    @staticmethod
    def path(pth) -> str:
        return os.path.join(Persist.workdir, 'store', pth)

    @staticmethod
    def storedir() -> str:
        return os.path.join(Persist.workdir, "store", "")


def files() -> []:
    res = []
    path = Persist.storedir()
    if os.path.exists(path):
        res = os.listdir(path)
    return res


def find(mtc, selector=None) -> []:
    if selector is None:
        selector = {}
    for fnm in fns(mtc):
        obj = hook(fnm)
        if '__deleted__' in obj:
            continue
        if selector and not search(obj, selector):
            continue
        yield obj


def fnclass(pth) -> str:
    try:
        *_rest, mpth = pth.split("store")
        splitted = mpth.split(os.sep)
        return splitted[0]
    except ValueError:
        pass
    return None


def fns(mtc) -> []:
    dname = ''
    lst = mtc.lower().split(".")[-1]
    for rootdir, dirs, _files in os.walk(Persist.storedir(), topdown=False):
        if dirs:
            dname = sorted(dirs)[-1]
            if dname.count('-') == 2:
                ddd = os.path.join(rootdir, dname)
                fls = sorted(os.listdir(ddd))
                if fls:
                    path2 = os.path.join(ddd, fls[-1])
                    splitted = strip(path2).split(os.sep, maxsplit=1)[0]
                    if lst in splitted.lower().split(".")[-1]:
                        yield strip(path2)


def fntime(daystr) -> float:
    daystr = daystr.replace('_', ':')
    datestr = ' '.join(daystr.split(os.sep)[-2:])
    if '.' in datestr:
        datestr, rest = datestr.rsplit('.', 1)
    else:
        rest = ''
    tme = time.mktime(time.strptime(datestr, '%Y-%m-%d %H:%M:%S'))
    if rest:
        tme += float('.' + rest)
    else:
        tme = 0
    return tme


def hook(otp) -> type:
    clz = fnclass(otp)
    splitted = clz.split(".")
    modname = ".".join(splitted[:1])
    clz = splitted[-1]
    mod = sys.modules.get(modname, None)
    if mod:
        cls = getattr(mod, clz, None)
    if cls:
        obj = cls()
        read(obj, otp)
        return obj
    obj = Object()
    read(obj, otp)
    return obj


# METHODS


def last(obj, selector=None) -> None:
    if selector is None:
        selector = {}
    result = sorted(
                    find(kind(obj), selector),
                    key=lambda x: fntime(x.__oid__)
                   )
    if result:
        inp = result[-1]
        update(obj, inp)
        obj.__oid__ = inp.__oid__
    return obj.__oid__


def read(obj, pth) -> str:
    pth = Persist.path(pth)
    with disklock:
        with open(pth, 'r', encoding='utf-8') as ofile:
            data = load(ofile)
            update(obj, data)
    obj.__oid__ = strip(pth)
    return obj.__oid__


def search(self, selector) -> bool:
    res = False
    for key, value in items(selector):
        try:
            val = self[key]
            if str(value) in str(val):
                res = True
                break
        except KeyError:
            continue
    return res


def write(obj) -> str:
    try:
        pth = obj.__oid__
    except TypeError:
        pth = ident(obj)
    pth = Persist.path(pth)
    cdir(pth)
    with disklock:
        with open(pth, 'w', encoding='utf-8') as ofile:
            dump(obj, ofile)
    return strip(pth)
