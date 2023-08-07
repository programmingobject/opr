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


def clear(self):
    self.__dict__ = {}


def copy(self, obj2):
    self.__dict__.update(obj2.__dict__)


def construct(self, *args, **kwargs):
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


def fromkeys(self, keyz, value):
    for key in keyz:
        self[key] = value


def get(self, key, default=None):
    return getattr(self, key, default)


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
