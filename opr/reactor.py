# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0212,W0718


"reacting"


import queue
import ssl
import threading


from .errored import Errors
from .evented import Event
from .objects import Object
from .threads import launch


def __dir__():
    return (
            'Reactor',
           )


__all__ = __dir__()


class Reactor(Object):

    def __init__(self):
        Object.__init__(self)
        self.cbs = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()

    def announce(self, txt) -> None:
        self.raw(txt)

    @staticmethod
    def dispatch(func, evt) -> None:
        try:
            func(evt)
        except Exception as ex:
            exc = ex.with_traceback(ex.__traceback__)
            Errors.errors.append(exc)
            try:
                evt.ready()
            except AttributeError:
                pass

    def event(self, txt) -> Event:
        msg = Event()
        msg.type = 'event'
        msg.orig = repr(self)
        msg.txt = txt
        return msg

    def handle(self, evt) -> Event:
        func = getattr(self.cbs, evt.type, None)
        if func:
            evt._thr = launch(Reactor.dispatch, func, evt, name=evt.cmd)
            evt._thr.join()
        return evt

    def loop(self) -> None:
        while not self.stopped.is_set():
            try:
                self.handle(self.poll())
            except (ssl.SSLError, EOFError) as ex:
                Errors.handle(ex)
                self.restart()

    def one(self, txt) -> Event:
        return self.handle(self.event(txt))

    def poll(self) -> Event:
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
