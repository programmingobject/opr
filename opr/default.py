# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903,R0902


"default"


from .objects import Object


def __dir__():
    return (
            'Default',
           )


__all__ = __dir__()


class Default(Object):

    __default__ = ""

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return Default.__default__
