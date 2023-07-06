# This file is placed in the Public Domain.


"clean namespace"


# IMPORTS


import datetime
import json
import os
import uuid
import _thread


# DEFINES


def __dir__():
    return (
            'Object',
            'ObjectDecoder',
            'ObjectEncoder',
            'copy',
            'dump',
            'dumps',
            'edit',
            'ident',
            'items',
            'keys',
            'kind',
            'load',
            'loads',
            'prt',
            'update',
            'values'
           )


__all__ = __dir__()


disklock = _thread.allocate_lock()


# CLASSES


class Object:

    "clean namespace"

    __slots__ = ('__dict__', '__oid__')

    def __init__(self):
        ""
        self.__oid__ = ident(self)

    def __contains__(self, key):
        ""
        return key in self.__dict__

    def __delitem__(self, key):
        ""
        return self.__dict__.__delitem__(key)

    def __getitem__(self, key):
        ""
        return self.__dict__.__getitem__(key)

    def __iter__(self):
        ""
        return iter(self.__dict__)

    def __len__(self):
        ""
        return len(self.__dict__)

    def __setitem__(self, key, value):
        ""
        return self.__dict__.__setitem__(key, value)


class Default(Object):

    "default return values"

    __slots__ = ("__default__",)

    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.__default__ = ""

    def __getattr__(self, key):
        ""
        return self.__dict__.get(key, self.__default__)

    def __setdefault__(self, default):
        ""
        self.__default__ = default


# METHODS


def copy(obj, val) -> None:
    "copy constructor"
    if isinstance(val, list):
        update(obj, dict(val))
    elif isinstance(val, zip):
        update(obj, dict(val))
    elif isinstance(val, dict):
        update(obj, val)
    elif isinstance(val, Object):
        update(obj, vars(val))
    return obj


def diff(obj, obj2):
    "return objects with different fields"
    result = {}
    for key, value in obj2.items():
        if key in obj and obj[key] != value:
            result[key] = value
        else:
            result[key] = value
    return result


def edit(obj, setter, skip=False):
    "change object values with values from a setter dict"
    try:
        setter = vars(setter)
    except (TypeError, ValueError):
        pass
    if not setter:
        setter = {}
    count = 0
    for key, val in setter.items():
        if skip and val == "":
            continue
        count += 1
        try:
            setattr(obj, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(obj, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(obj, key, True)
        elif val in ["False", "false"]:
            setattr(obj, key, False)
        else:
            setattr(obj, key, val)
    return count


def ident(obj) -> str:
    "create ident for object"
    return os.path.join(
                        kind(obj),
                        str(uuid.uuid4().hex),
                        os.sep.join(str(datetime.datetime.now()).split())
                       )


def items(obj) -> []:
    "key/value pairs"
    if isinstance(obj, type({})):
        return obj.items()
    return obj.__dict__.items()


def keys(obj) -> []:
    "list of keys"
    return obj.__dict__.keys()


def kind(obj) -> str:
    "type of object"
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = obj.__name__
    return kin


def prt(obj, args="", skip="", plain=False):
    "pretty object print"
    res = []
    keyz = []
    if "," in args:
        keyz = args.split(",")
    if not keyz:
        keyz = keys(obj)
    for key in sorted(keyz):
        if key.startswith("_"):
            continue
        if skip:
            skips = skip.split(",")
            if key in skips:
                continue
        value = getattr(obj, key, None)
        if not value:
            continue
        if " object at " in str(value):
            continue
        txt = ""
        if plain:
            value = str(value)
            txt = f'{value}'
        elif isinstance(value, str) and len(value.split()) >= 2:
            txt = f'{key}="{value}"'
        else:
            txt = f'{key}={value}'
        res.append(txt)
    txt = " ".join(res)
    return txt.strip()


def update(obj, data, empty=True) -> None:
    "update an object with a data dictionary"
    for key, value in items(data):
        if not empty and not value:
            continue
        setattr(obj, key, value)


def values(obj) -> []:
    "list of values"
    return obj.__dict__.values()


## DECODER


class ObjectDecoder(json.JSONDecoder):

    "convert string to object"

    def decode(self, s, _w=None) -> Object:
        "string to object"
        val = json.JSONDecoder.decode(self, s)
        if not val:
            val = {}
        obj = Object()
        copy(obj, val)
        return obj

    def raw_decode(self, s, idx=0) -> (int, Object):
        "do a indexed conversion"
        return json.JSONDecoder.raw_decode(self, s, idx)


def load(fpt, *args, **kw) -> Object:
    "return object from filepath"
    return json.load(fpt, *args, cls=ObjectDecoder, **kw)


def loads(string, *args, **kw) -> Object:
    "load object from string"
    return json.loads(string, *args, cls=ObjectDecoder, **kw)


# ENCODER


class ObjectEncoder(json.JSONEncoder):

    "from object to string"

    def default(self, o) -> str:
        "return string version for object"
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        if isinstance(
                      o,
                      (
                       type(str),
                       type(True),
                       type(False),
                       type(int),
                       type(float)
                      )
                     ):
            return str(o)
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return str(o)

    def encode(self, o) -> str:
        "convert object to string"
        return json.JSONEncoder.encode(self, o)

    def iterencode(self, o, _one_shot=False) -> str:
        "use multiple encoding passes"
        return json.JSONEncoder.iterencode(self, o, _one_shot)


def dump(*args, **kw) -> None:
    "json dump to disk with object encoder"
    kw["cls"] = ObjectEncoder
    return json.dump(*args, **kw)


def dumps(*args, **kw) -> str:
    "json dump to string with object encoder"
    kw["cls"] = ObjectEncoder
    return json.dumps(*args, **kw)
