# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903


"persistence"


import inspect
import os
import sys


from .decoder import hook, load
from .encoder import dump
from .locking import disklock, hooklock
from .objects import Object, keys, update
from .persist import Persist, ident, kind
from .utility import cdir, fnclass, fntime, nme, search, strip


def __dir__():
    return (
            'NoClass',
            'Storage',
            'last',
            'read',
            'write'
           )


__all__ = __dir__()


class NoClass(Exception):

    pass


class Storage(Object):

    classes = Object()
    workdir = os.path.expanduser(f'~/.{nme()}')

    @staticmethod
    def add(clz):
        if not clz:
            return
        name = str(clz).split()[1][1:-2]
        Storage.classes[name] = clz

    @staticmethod
    def long(name):
        split = name.split(".")[-1].lower()
        res = None
        for named in keys(Storage.classes):
            if split in named.split(".")[-1].lower():
                res = named
                break
        return res

    @staticmethod
    def path(pth):
        return os.path.join(Storage.store(), pth)

    @staticmethod
    def scan(mod) -> None:
        for key, clz in inspect.getmembers(mod, inspect.isclass):
            if key.startswith("cb"):
                continue
            if not issubclass(clz, Persist):
                continue
            Storage.add(clz)

    @staticmethod
    def store(pth=""):
        return os.path.join(Storage.workdir, "store", pth)


def files() -> []:
    return os.listdir(Storage.store())


def find(mtc, selector=None) -> []:
    if selector is None:
        selector = {}
    for fnm in reversed(sorted(fns(mtc), key=fntime)):
        clzname = fnclass(fnm)
        clz = sys.modules.get(clzname, None)
        if not clz:
            clz = Persist
        obj = clz()
        read(obj, fnm) 
        if '__deleted__' in obj:
            continue
        if selector and not search(obj, selector):
            continue
        yield obj


def fns(mtc) -> []:
    assert Storage.workdir
    dname = ''
    clz = Storage.long(mtc)
    if not clz:
        raise NoClass(mtc)
    path = Storage.path(clz)
    for rootdir, dirs, _files in os.walk(path, topdown=False):
        if dirs:
            dname = sorted(dirs)[-1]
            if dname.count('-') == 2:
                ddd = os.path.join(rootdir, dname)
                fls = sorted(os.listdir(ddd))
                if fls:
                    yield strip(os.path.join(ddd, fls[-1]))


def last(self, selector=None) -> None:
    if selector is None:
        selector = {}
    result = sorted(
                    find(kind(self), selector),
                    key=lambda x: fntime(x.__oid__)
                   )
    if result:
        inp = result[-1]
        update(self, inp)
        self.__oid__ = inp.__oid__
    return self.__oid__


def read(self, pth) -> str:
    with disklock:
        pth = os.path.join(Storage.store(), pth)
        with open(pth, 'r', encoding='utf-8') as ofile:
            data = load(ofile)
            update(self, data)
        self.__oid__ = strip(pth)
        return self.__oid__


def write(self) -> str:
    with disklock:
        try:
            pth = self.__oid__
        except (AttributeError, TypeError):
            pth = ident(self)
        pth = os.path.join(Storage.store(), pth)
        cdir(pth)
        with open(pth, 'w', encoding='utf-8') as ofile:
            dump(self, ofile)
        return os.sep.join(pth.split(os.sep)[-4:])
