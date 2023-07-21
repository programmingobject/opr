# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,E0402


"recursive functions"


from .objects import Object, items, update
from .persist import read, write


def __dir__():
    return (
            'readrec',
            'writerec'
           )


__all__ = __dir__()


def readrec(obj, pth=None) -> type:
    ooo = type(obj)()
    if pth:
        read(ooo, pth)
    else:
        update(ooo, obj)
    oooo = type(obj)()
    for key, value in items(ooo):
        if issubclass(type(value), Object):
            oooo[key] = readrec(value)
            continue
        oooo[key] = value
    return oooo


def writerec(obj):
    ooo = type(obj)()
    for key, value in items(obj):
        if issubclass(type(value), Object):
            ooo[key] = writerec(value)
        else:
            ooo[key] = str(value)
        continue
    return write(ooo)
