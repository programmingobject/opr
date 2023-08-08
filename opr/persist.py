# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,R0903


"data storage"


import datetime
import os
import uuid


from .objects import Object


def __dir__():
    return (
            'Persist',
            'ident',
            'kind'
           )


class Persist(Object):


    __slots__ = ("__oid__",)


    def __init__(self):
        Object.__init__(self)
        self.__oid__ = ident(self)


def ident(self) -> str:
    return os.path.join(
                        kind(self),
                        str(uuid.uuid4().hex),
                        os.path.join(*str(datetime.datetime.now()).split())
                       )


def kind(obj) -> str:
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = obj.__name__
    return kin
