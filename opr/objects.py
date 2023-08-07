# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903


"a clean namespace"


import datetime
import inspect
import json
import os
import pathlib
import sys
import time
import uuid
import _thread


from json import JSONDecoder, JSONEncoder


def __dir__():
    return (
            'Default',
            'Object',
            'Persist',
            'clear',
            'copy',
            'edit',
            'fromkeys',
            'get',
            'ident',
            'items',
            'keys',
            'kind',
            'pop',
            'popitem',
            'prt',
            'read',
            'search',
            'setdefault',
            'update',
            'values',
            'write'
           )


__all__ = __dir__()


disklock = _thread.allocate_lock()
hooklock = _thread.allocate_lock()


class NoClass(Exception):

    pass


"object"


class Object:

    __slots__ = ("__dict__", "__oid__")

    def __init__(self, *args, **kwargs):
        self.__oid__ = ident(self)
        if args:
            val = args[0]
            if isinstance(val, list):
                update(self, dict(val))
            elif isinstance(val, zip):
                update(self, dict(val))
            elif isinstance(val, dict):
                update(self, val)
            elif isinstance(val, Object):
                update(self, vars(val))
        if kwargs:
            update(self, kwargs)

    def __contains__(self, key):
        return key in self.__dict__

    def __delitem__(self, key):
        return self.__dict__.__delitem__(key)

    def __getitem__(self, key):
        return self.__dict__.__getitem__(key)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __setitem__(self, key, value):
        return self.__dict__.__setitem__(key, value)

    def __str__(self):
        res = "{"
        for key, value in items(self):
            if issubclass(type(value), Object):
                cur = str(value)
                res += f"'{key}': {cur}, "
            else:
                res += f"'{key}': '{value}', "
        if len(res) > 2:
            res = res[:-2]
        res += "}"
        return res


class Default(Object):

    __slots__ = ("__default__",)

    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.__default__ = ""

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return self.__default__


def clear(self):
    self.__dict__ = {}


def copy(self, obj2):
    self.__dict__.update(obj2.__dict__)


def edit(self, setter, skip=False):
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
            setattr(self, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(self, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(self, key, True)
        elif val in ["False", "false"]:
            setattr(self, key, False)
        else:
            setattr(self, key, val)
    return count


def fromkeys(self, keyz, value):
    for key in keyz:
        self[key] = value


def get(self, key, default=None):
    return getattr(self, key, default)


def ident(self) -> str:
    return os.path.join(
                        kind(self),
                        str(uuid.uuid4().hex),
                        os.sep.join(str(datetime.datetime.now()).split())
                       )


def items(self) -> []:
    if isinstance(self, type({})):
        return self.items()
    return self.__dict__.items()


def keys(self) -> []:
    return self.__dict__.keys()


def kind(self) -> str:
    kin = str(type(self)).split()[-1][1:-2]
    if kin == "type":
        kin = self.__name__
    return kin


def pop(self, key, default=None):
    if key in self:
        val = self[key]
        del self[key]
        return val
    if default:
        return default
    raise KeyError(key)


def popitem(self):
    if not self:
        raise KeyError
    for key, value in items(self):
        yield key, value


def prt(self, args="", skip="", plain=False):
    res = []
    keyz = []
    if "," in args:
        keyz = args.split(",")
    if not keyz:
        keyz = keys(self)
    for key in sorted(keyz):
        if key.startswith("_"):
            continue
        if skip and doskip(key, skip):
            continue
        value = getattr(self, key, None)
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


def setdefault(self, key, default):
    if key not in self:
        self[key] = default
    return self[key]


def update(self, data, empty=True) -> None:
    for key, value in items(data):
        if empty and not value:
            continue
        self[key] = value


def values(self) -> []:
    return self.__dict__.values()


"json"


class ObjectDecoder(JSONDecoder):

    def __init__(self, *args, **kwargs):
        ""
        JSONDecoder.__init__(self, *args, **kwargs)

    def decode(self, s, _w=None):
        ""
        val = JSONDecoder.decode(self, s)
        if not val:
            val = {}
        return Object(val)

    def raw_decode(self, s, idx=0):
        ""
        return JSONDecoder.raw_decode(self, s, idx)


class ObjectEncoder(JSONEncoder):

    def __init__(self, *args, **kwargs):
        ""
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o) -> str:
        ""
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
            return o
        try:
            return JSONEncoder.default(self, o)
        except TypeError:
            return str(o)

    def encode(self, o) -> str:
        ""
        return JSONEncoder.encode(self, o)

    def iterencode(
                   self,
                   o,
                   _one_shot=False
                  ) -> str:
        ""
        return JSONEncoder.iterencode(self, o, _one_shot)


def dump(*args, **kw) -> None:
    kw["cls"] = ObjectEncoder
    return json.dump(*args, **kw)


def dumps(*args, **kw) -> str:
    kw["cls"] = ObjectEncoder
    return json.dumps(*args, **kw)


def load(fpt, *args, **kw):
    return json.load(fpt, *args, cls=ObjectDecoder, **kw)


def loads(string, *args, **kw):
    return json.loads(string, *args, cls=ObjectDecoder, **kw)


"persistence"


class Persist:

    classes = Object()
    workdir = ".opr"

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


"utility"


def cdir(pth) -> None:
    if not pth.endswith(os.sep):
        pth = os.path.dirname(pth)
    pth = pathlib.Path(pth)
    os.makedirs(pth, exist_ok=True)


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


def doskip(txt, skipping) -> bool:
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
