# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903


"object decoder"


import json


from json import JSONDecoder


from .objects import construct
from .storage import Data


class ObjectDecoder(JSONDecoder):

    def __init__(self, *args, **kwargs):
        ""
        JSONDecoder.__init__(self, *args, **kwargs)

    def decode(self, s, _w=None):
        ""
        val = JSONDecoder.decode(self, s)
        if not val:
            val = {}
        data = Data()
        construct(data, val)
        return data

    def raw_decode(self, s, idx=0):
        ""
        return JSONDecoder.raw_decode(self, s, idx)



def load(fpt, *args, **kw):
    return json.load(fpt, *args, cls=ObjectDecoder, **kw)


def loads(string, *args, **kw):
    return json.loads(string, *args, cls=ObjectDecoder, **kw)
