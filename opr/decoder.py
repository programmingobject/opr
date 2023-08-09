# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903


"object decoder"


import json
import sys


from json import JSONDecoder


from .locking import hooklock, jsonlock
from .objects import Object, construct
from .threads import name


def __dir__():
    return (
            'ObjectDecoder',
            'load',
            'loads'
           )


__all__ = __dir__()


class ObjectDecoder(JSONDecoder):

    def __init__(self, *args, **kwargs):
        ""
        JSONDecoder.__init__(self, *args, **kwargs)

    def decode(self, s, _w=None):
        ""
        with jsonlock:
            val = JSONDecoder.decode(self, s)
            if not val:
                val = {}
            return hook(val)

    def raw_decode(self, s, idx=0):
        ""
        return JSONDecoder.raw_decode(self, s, idx)


def hook(objdict) -> type:
    with hooklock:
        cls = Object
        if "__type__" in objdict:
            clz = objdict["__type__"]
            del objdict["__type__"]
            splitted = clz.split(".")
            modname = ".".join(splitted[:1])
            clz = splitted[-1]
            mod = sys.modules.get(modname, None)
            if mod:
                cls = getattr(mod, clz, cls)
        obj = cls()
        construct(obj, objdict)
        return obj


def load(fpt, *args, **kw):
    kw["cls"] = ObjectDecoder
    kw["object_hook"] = hook
    return json.load(fpt, *args, **kw)


def loads(string, *args, **kw):
    kw["cls"] = ObjectDecoder
    kw["object_hook"] = hook
    return json.loads(string, *args, **kw)
