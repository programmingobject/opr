# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903


"object encoder"


import json


from json import JSONEncoder


from .threads import name


def __dir__():
    return (
            'ObjectEncoder',
            'dump',
            'dumps'
           )


__all__ = __dir__()


class ObjectEncoder(JSONEncoder):

    def __init__(self, *args, **kwargs):
        ""
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o) -> str:
        ""
        o.__type__ = name(o)
        try:
            return o.items()
        except AttributeError:
            pass
        try:
            return vars(o)
        except ValueError:
            pass
        try:
            return iter(o)
        except ValueError:
            pass
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
            return repr(o)

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
