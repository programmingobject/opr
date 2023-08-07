# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0212,W0718,E0402


"reactor"


import queue
import ssl
import sys
import threading


from .errored import Errors
from .message import Event
from .threads import launch
from .utility import spl


def __dir__():
    return (
            'Reactor',
           )


__all__ = __dir__()


class Reactor:

    errors = []

    def __init__(self):
        self.cbs = {}
        self.queue = queue.Queue()
        self.stopped = threading.Event()

    def announce(self, txt) -> None:
        self.raw(txt)

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
        msg.orig = repr(self)
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

    def init(self, mods):
        for modname in spl(mods):
            oprmod = sys.modules.get("modules", None)
            mod = getattr(oprmod, modname, None)
            if mod and "init" in dir(mod):
                mod.init(self)

    def loop(self) -> None:
        while not self.stopped.is_set():
            try:
                self.handle(self.poll())
            except (ssl.SSLError, EOFError) as ex:
                exc = ex.with_traceback(ex.__traceback__)
                Errors.errors.append(exc)
                self.restart()

    def one(self, txt):
        return self.handle(self.event(txt))

    def poll(self):
        return self.queue.get()

    def put(self, evt) -> None:
        self.queue.put_nowait(evt)

    def raw(self, txt) -> None:
        pass

    def say(self, channel, txt) -> None:
        if channel:
            self.raw(txt)

    def register(self, typ, func) -> None:
        self.cbs[typ] = func

    def restart(self) -> None:
        self.stop()
        self.start()

    def start(self) -> None:
        launch(self.loop)

    def stop(self) -> None:
        self.stopped.set()
        self.queue.put_nowait(None)
