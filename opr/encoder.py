# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"encoding objects"


import json


from .objects import Object


def __dir__():
    return (
            'ObjectEncoder',
            'dump',
            'dumps',
           )


__all__ = __dir__()


class ObjectEncoder(json.JSONEncoder):

    def __init__(self, *args, **kwargs):
        ""
        json.JSONEncoder.__init__(self, *args, **kwargs)

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
            return str(o)
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return str(o)

    def encode(self, o) -> str:
        ""
        return json.JSONEncoder.encode(self, o)

    def iterencode(
                   self,
                   o,
                   _one_shot=False
                  ) -> str:
        ""
        return json.JSONEncoder.iterencode(self, o, _one_shot)


def dump(*args, **kw) -> None:
    kw["cls"] = ObjectEncoder
    return json.dump(*args, **kw)


def dumps(*args, **kw) -> str:
    kw["cls"] = ObjectEncoder
    return json.dumps(*args, **kw)
