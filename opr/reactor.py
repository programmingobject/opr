# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0212,W0718,E0402


"reactor"


import queue
import ssl
import threading


from .errored import Errors
from .message import Event
from .objects import Object
from .threads import launch


def __dir__():
    return (
            'Reactor',
           )


__all__ = __dir__()


class Reactor(Object):

    errors = []

    def __init__(self):
        self.cbs = {}
        self.queue = queue.Queue()
        self.stopped = threading.Event()

    @staticmethod
    def dispatch(func, evt) -> None:
        try:
            func(evt)
        except Exception as exc:
            Errors.handle(exc)
            try:
                evt.ready()
            except AttributeError:
                pass

    def event(self, txt):
        msg = Event()
        msg.type = 'event'
        msg.orig = object.__repr__(self)
        msg.txt = txt
        return msg

    def handle(self, evt):
        func = self.cbs.get(evt.type, None)
        if func:
            evt._thr = launch(
                              Reactor.dispatch,
                              func,
                              evt,
                              name=evt.cmd or evt.type
                             )
        return evt

    def loop(self) -> None:
        while not self.stopped.is_set():
            try:
                self.handle(self.poll())
            except (ssl.SSLError, EOFError) as ex:
                exc = ex.with_traceback(ex.__traceback__)
                Errors.errors.append(exc)
                self.stopped.set()
                launch(self.loop)

    def poll(self):
        return self.queue.get()

    def put(self, evt) -> None:
        self.queue.put_nowait(evt)

    def register(self, typ, func) -> None:
        self.cbs[typ] = func
