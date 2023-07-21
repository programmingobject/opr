# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"object brokers"


from .objects import Object


def __dir__():
    return (
            "Broker",
           )


__all__ = __dir__()


class Broker(Object):

    objs = []

    @staticmethod
    def add(obj) -> None:
        Broker.objs.append(obj)

    @staticmethod
    def announce(txt) -> None:
        for obj in Broker.objs:
            obj.announce(txt)

    @staticmethod
    def byorig(orig) -> Object:
        for obj in Broker.objs:
            if repr(obj) == orig:
                return obj
        return None

    @staticmethod
    def remove(obj) -> None:
        try:
            Broker.objs.remove(obj)
        except ValueError:
            pass

    @staticmethod
    def say(orig, txt, channel=None) -> None:
        obj = Broker.byorig(orig)
        if obj:
            if channel:
                obj.say(channel, txt)
            else:
                obj.raw(txt)
