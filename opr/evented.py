# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,E0402


"events happen"


import threading


from .brokers import Broker
from .objects import Object
from .parsers import parse


def __dir__():
    return (
            "Event",
           )


__all__ = __dir__()


class Event(Object):

    __slots__ = ('_ready', '_thr')

    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self._ready = threading.Event()
        self._thr = None
        self.orig = ""
        self.result = []
        self.txt = ""
        self.type = "event"

    def bot(self):
        assert self.orig
        return Broker.byorig(self.orig)

    def parse(self):
        parse(self, self.txt)

    def ready(self) -> None:
        self._ready.set()

    def reply(self, txt) -> None:
        self.result.append(txt)

    def show(self) -> None:
        for txt in self.result:
            Broker.say(self.orig, txt, self.channel)

    def wait(self) -> []:
        if self.thr:
            self.thr.join()
        self._ready.wait()
        return self.result
