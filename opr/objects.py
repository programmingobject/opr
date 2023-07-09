# This file is placed in the Public Domain.


"""clean namespace"""


__author__ = "Bart Thate <programmingobject@gmail.com>"


# IMPORTS


import datetime
import json
import os
import pathlib
import sys
import time
import uuid
import _thread


# INTERFACE


def __dir__():
    return (
            'Persist',
            'Object',
            'copy',
            'edit',
            'find',
            'ident',
            'items',
            'keys',
            'kind',
            'last',
            'prt',
            'read',
            'readrec',
            'search',
            'update',
            'values',
            'write',
            'writerec'
           )


__all__ = __dir__()


# DEFINES


disklock = _thread.allocate_lock()


# OBJECT


class Object:

    """doesn't have any methods, just dunders"""

    __slots__ = ('__default__', '__dict__', '__oid__')

    def __init__(self):
        """construct an object without any methods, just dunders"""
        self.__default__ = ""
        self.__oid__ = ident(self)

    def __contains__(self, key):
        """object contains key"""
        return key in self.__dict__

    def __delitem__(self, key):
        """remove key from object"""
        return self.__dict__.__delitem__(key)

    def __getattr__(self, key):
        ""
        return self.__dict__.get(key, self.__default__)

    def __getitem__(self, key):
        """dict like access"""
        return self.__dict__.__getitem__(key)

    def __iter__(self):
        """iterate over this object"""
        return iter(self.__dict__)

    def __len__(self):
        """number of elements"""
        return len(self.__dict__)

    def __setitem__(self, key, value):
        """dict like set"""
        return self.__dict__.__setitem__(key, value)

    def __str__(self):
        """return recursive json string"""
        return dumps(dumprec(self))


def copy(obj, val) -> None:
    """copy constructor"""
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
    """return objects with different fields"""
    result = {}
    for key, value in obj2.items():
        if key in obj and obj[key] != value:
            result[key] = value
        else:
            result[key] = value
    return result


def dumprec(obj) -> str:
    """read object recursively"""
    ooo = type(obj)()
    update(ooo, obj)
    oooo = type(obj)()
    for key, value in items(ooo):
        if issubclass(type(value), Object):
            oooo[key] = dumprec(value)
            continue
        oooo[key] = value
    return oooo


def edit(obj, setter, skip=False):
    """change object values with values from a setter dict"""
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
    """create ident for object"""
    return os.path.join(
                        kind(obj),
                        str(uuid.uuid4().hex),
                        os.sep.join(str(datetime.datetime.now()).split())
                       )


def items(obj) -> []:
    """key/value pairs"""
    if isinstance(obj, type({})):
        return obj.items()
    return obj.__dict__.items()


def keys(obj) -> []:
    """list of keys"""
    return obj.__dict__.keys()


def kind(obj) -> str:
    """type of object"""
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = obj.__name__
    return kin


def prt(obj, args="", skip="", plain=False):
    """pretty object print"""
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


def search(obj, selector) -> bool:
    """check whether values in selector dict match in the object"""
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


def update(obj, data, empty=True) -> None:
    """update an object with a data dictionary"""
    for key, value in items(data):
        if not empty and not value:
            continue
        setattr(obj, key, value)


def values(obj) -> []:
    """list of values"""
    return obj.__dict__.values()


# DECODER


class ObjectDecoder(json.JSONDecoder):

    """convert string to object"""

    def __init__(self, *args, **kwargs):
        ""
        json.JSONDecoder.__init__(self, *args, **kwargs)

    def decode(self, s, _w=None):
        """string to object"""
        val = json.JSONDecoder.decode(self, s)
        if not val:
            val = {}
        obj = Object()
        copy(obj, val)
        return obj

    def raw_decode(self, s, idx=0):
        """do a indexed conversion"""
        return json.JSONDecoder.raw_decode(self, s, idx)


def load(fpt, *args, **kw) :
    """return object from filepath"""
    return json.load(fpt, *args, cls=ObjectDecoder, **kw)


def loads(string, *args, **kw):
    """load object from string"""
    return json.loads(string, *args, cls=ObjectDecoder, **kw)


# ENCODER


class ObjectEncoder(json.JSONEncoder):

    """from object to string"""

    def __init__(self, *args, **kwargs):
        ""
        json.JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o) -> str:
        """return string version for object"""
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
        """convert object to string"""
        return json.JSONEncoder.encode(self, o)

    def iterencode(self, o, _one_shot=False) -> str:
        """use multiple encoding passes"""
        return json.JSONEncoder.iterencode(self, o, _one_shot)


def dump(*args, **kw) -> None:
    """json dump to disk with object encoder"""
    kw["cls"] = ObjectEncoder
    return json.dump(*args, **kw)


def dumps(*args, **kw) -> str:
    """json dump to string with object encoder"""
    kw["cls"] = ObjectEncoder
    return json.dumps(*args, **kw)


# PERSIST


class Persist:

    """directory to persist to"""

    workdir = ""

    @staticmethod
    def path(pth) -> str:
        """return store path"""
        return os.path.join(Persist.workdir, 'store', pth)

    @staticmethod
    def storedir() -> str:
        """return storage directory"""
        return os.path.join(Persist.workdir, "store")


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


def files() -> []:
    """show all files in store"""
    res = []
    path = Persist.storedir()
    if os.path.exists(path):
        res = os.listdir(path)
    return res


def find(mtc, selector=None) -> []:
    """locate specific objects"""
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
    """return class from filename"""
    try:
        *_rest, mpth = pth.split("store")
        splitted = mpth.split(os.sep)
        return splitted[0]
    except ValueError:
        pass
    return None


def fns(mtc) -> []:
    """return matching filenames"""
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
    """return time from filename"""
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
    """return object from filename"""
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


def spl(txt) -> []:
    """split comma seperated string"""
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


## METHODS


def last(obj, selector=None) -> None:
    """update with last saved version"""
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
    """read object from path"""
    pth = Persist.path(pth)
    with disklock:
        with open(pth, 'r', encoding='utf-8') as ofile:
            data = load(ofile)
            update(obj, data)
    obj.__oid__ = strip(pth)
    return obj.__oid__


def readrec(obj, pth=None) -> type:
    """read object recursively"""
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


def write(obj) -> str:
    """write object to disk"""
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
    """write object recursively"""
    ooo = type(obj)()
    for key, value in items(obj):
        if issubclass(type(value), Object):
            setattr(ooo, key, writerec(value))
        else:
            setattr(ooo, key, str(value))
    return write(ooo)
