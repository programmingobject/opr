# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903


"persistence"


import datetime
import inspect
import os
import sys
import uuid


from .decoder import load
from .encoder import dump
from .locking import disklock, hooklock
from .objects import Object, keys, search, update
from .storage import ident, kind
from .utility import cdir, fntime, strip


class NoClass(Exception):

     pass


class Persist(Object):

    classes = Object()
    workdir = ""

    @staticmethod
    def add(clz):
        if not clz:
            return
        name = str(clz).split()[1][1:-2]
        Persist.classes[name] = clz

    @staticmethod
    def long(nme):
        split = nme.split(".")[-1].lower()
        res = None
        for name in keys(Persist.classes):
            if split in name.split(".")[-1].lower():
                res = name
                break
        return res

    @staticmethod
    def path(pth):
        return os.path.join(Persist.store(), pth)

    @staticmethod
    def scan(mod) -> None:
        for key, clz in inspect.getmembers(mod, inspect.isclass):
            if key.startswith("cb"):
                continue
            if not issubclass(clz, Object):
                continue
            Persist.add(clz)

    @staticmethod
    def store(pth=""):
        return os.path.join(Persist.workdir, "store", pth)


def ident(self) -> str:
    return "/".join(
                    kind(self),
                    str(uuid.uuid4().hex),
                    "/".join(str(datetime.datetime.now()).split())
                   )


def files() -> []:
    return os.listdir(Persist.store())


def find(mtc, selector=None) -> []:
    if selector is None:
        selector = {}
    for fnm in reversed(sorted(fns(mtc), key=fntime)):
        ppth = os.path.join(mtc, fnm)
        obj = hook(ppth)
        if '__deleted__' in obj:
            continue
        if selector and not search(obj, selector):
            continue
        yield obj


def fns(mtc) -> []:
    assert Persist.workdir
    dname = ''
    clz = Persist.long(mtc)
    if not clz:
        raise NoClass(mtc)
    path = os.path.join(Persist.store(), clz)
    for rootdir, dirs, _files in os.walk(path, topdown=False):
        if dirs:
            dname = sorted(dirs)[-1]
            if dname.count('-') == 2:
                ddd = os.path.join(rootdir, dname)
                fls = sorted(os.listdir(ddd))
                if fls:
                    yield os.path.join(ddd, fls[-1])


def hook(pth) -> type:
    with hooklock:
        clz = pth.split(os.sep)[-4]
        splitted = clz.split(".")
        modname = ".".join(splitted[:1])
        clz = splitted[-1]
        mod = sys.modules.get(modname, None)
        if mod:
            cls = getattr(mod, clz, None)
        if cls:
            obj = cls()
            read(obj, pth)
            return obj
        obj = Object()
        read(obj, pth)
        return obj


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
        pth = Persist.store(strip(pth))
        with open(pth, 'r', encoding='utf-8') as ofile:
            data = load(ofile)
            update(self, data)
        self.__oid__ = strip(pth)
        return self.__oid__


def write(self) -> str:
    with disklock:
        try:
            pth = self.__oid__
        except TypeError:
            pth = ident(self)
        pth = os.path.join(Persist.workdir, "store", pth)
        cdir(pth)
        with open(pth, 'w', encoding='utf-8') as ofile:
            dump(self, ofile)
        return os.sep.join(pth.split(os.sep)[-4:])
