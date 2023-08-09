# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903


"a clean namespace"



class Object:

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
        return dumps(self.__dict__)


def clear(obj):
    obj.__dict__ = {}


def copy(obj, obj2):
    obj.__dict__.update(obj2.__dict__)


def construct(obj, *args, **kwargs):
    if args:
        val = args[0]
        if isinstance(val, list):
            update(obj, dict(val))
        elif isinstance(val, zip):
            update(obj, dict(val))
        elif isinstance(val, dict):
            update(obj, val)
        elif isinstance(val, Object):
            update(obj, vars(val))
    if kwargs:
        update(obj, kwargs)


def fromkeys(obj, keyz, value):
    for key in keyz:
        obj[key] = value


def get(obj, key, default=None):
    return getattr(obj, key, default)


def items(obj) -> []:
    if isinstance(obj, type({})):
        return obj.items()
    return obj.__dict__.items()


def keys(obj) -> []:
    return obj.__dict__.keys()


def pop(obj, key, default=None):
    if key in obj:
        val = obj[key]
        del obj[key]
        return val
    if default:
        return default
    raise KeyError(key)


def popitem(obj):
    if not obj:
        raise KeyError
    for key, value in items(obj):
        yield key, value


def search(obj, selector) -> bool:
    res = False
    for key, value in items(selector):
        try:
            val = obj[key]
            if str(value) in str(val):
                res = True
                break
        except KeyError:
            continue
    return res


def setdefault(obj, key, default):
    if key not in obj:
        obj[key] = default
    return obj[key]


def update(obj, data, empty=True) -> None:
    for key, value in items(data):
        if empty and not value:
            continue
        obj[key] = value


def values(obj) -> []:
    return obj.__dict__.values()


from .encoder import dumps

