# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,E0402
# flake8: noqa=C901


"deconding objects"


import json


from .objects import Object


def __dir__():
    return (
            'ObjectDecoder',
            'load',
            'loads',
           )


__all__ = __dir__()


class ObjectDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        ""
        json.JSONDecoder.__init__(self, *args, **kwargs)

    def decode(self, s, _w=None):
        ""
        val = json.JSONDecoder.decode(self, s)
        if not val:
            val = {}
        return Object(val)

    def raw_decode(self, s, idx=0):
        ""
        return json.JSONDecoder.raw_decode(self, s, idx)


def load(fpt, *args, **kw):
    return json.load(fpt, *args, cls=ObjectDecoder, **kw )


def loads(string, *args, **kw):
    return json.loads(string, *args, cls=ObjectDecoder, **kw)
