# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903


"default"


from .storage import Data


class Default(Data):

    __slots__ = ("__default__",)

    def __init__(self, *args, **kwargs):
        Data.__init__(self, *args, **kwargs)
        self.__default__ = ""

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return self.__default__

