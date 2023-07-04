# This file is placed in the Public Domain.


"persist"


# IMPORTS


import os
import sys
import time
import _thread


from opr.objects import Object, copy, ident, dump, items, kind, load, update
from opr.utility import cdir, strip


# DEFINES


def __dir__():
    return (
            'Persist',
            'files',
            'find',
            'fnclass',
            'fns',
            'fntime',
            'hook',
            'last',
            'read',
            'readrec',
            'search',
            'write',
            'writerec'
           )


disklock = _thread.allocate_lock()


# CLASSES


class Persist(Object):

    "directory to persist to"

    workdir = ""

    @staticmethod
    def path(pth) -> str:
        "return store path"
        return os.path.join(Persist.workdir, 'store', pth)

    @staticmethod
    def storedir() -> str:
        "return storage directory"
        return os.path.join(Persist.workdir, "store")


# UTILITY


def files() -> []:
    "show all files in store"
    res = []
    path = Persist.storedir()
    if os.path.exists(path):
        res = os.listdir(path)
    return res


def find(mtc, selector=None) -> []:
    "locate specific objects"
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
    "return class from filename"
    try:
        *_rest, mpth = pth.split("store")
        splitted = mpth.split(os.sep)
        return splitted[0]
    except ValueError:
        pass
    return None


def fns(mtc) -> []:
    "return matching filenames"
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
    "return time from filename"
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
    "return object from filename"
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


## METHODS


def last(obj, selector=None) -> None:
    "update with last saved version"
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
    "read object from path"
    pth = Persist.path(pth)
    with disklock:
        with open(pth, 'r', encoding='utf-8') as ofile:
            data = load(ofile)
            update(obj, data)
    obj.__oid__ = strip(pth)
    return obj.__oid__


def readrec(obj, pth=None) -> type:
    "read object recursively"
    ooo = type(obj)()
    if pth:
        read(ooo, pth)
    else:
        update(ooo, obj)
    oooo = type(obj)()
    for key, value in items(ooo):
        if issubclass(type(value), Object):
            setattr(oooo, key, readrec(value))
            continue
        setattr(oooo, key, value)
    return oooo


def search(obj, selector) -> bool:
    "check whether values in selector dict match in the object"
    res = False
    select = Object()
    copy(select, selector)
    for key, value in items(select):
        try:
            val = getattr(obj, key)
        except AttributeError:
            continue
        if str(value) in str(val):
            res = True
            break
    return res


def write(obj) -> str:
    "write object to disk"
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


def writerec(obj):
    "write object recursively"
    ooo = type(obj)()
    for key, value in items(obj):
        if issubclass(type(value), Object):
            setattr(ooo, key, writerec(value))
        else:
            setattr(ooo, key, str(value))
    return write(ooo)
