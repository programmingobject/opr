# This file is placed in the Public Domain.


"""handler"""


# AUTHOR


__author__ = "Bart Thate <programmingobject@gmail.com>"
__version__ = 1


# IMPORTS


import inspect
import io
import os
import queue
import ssl
import sys
import threading
import traceback

from opr.loggers import Logging
from opr.objects import Default, Object, keys
from opr.threads import launch
from opr.utility import spl


# INTERFACE


def __dir__():
    return (
            'Bus',
            'Cfg',
            'Commands',
            'Errors',
            'Event',
            'Handler',
            "dispatch",
            'waiter'
           )

__all__ = __dir__()


# DEFINES


MODNAMES = {
           }

Cfg = Default()
Cfg.debug = False
Cfg.mod = ""
Cfg.verbose = False


# CLASSES


class Errors(Object):

    """list of errors"""

    errors = []

    @staticmethod
    def handle(ex) -> None:
        """store exception in the errors list"""
        exc = ex.with_traceback(ex.__traceback__)
        Errors.errors.append(exc)

    @staticmethod
    def size():
        """return number of errors"""
        return len(Errors.errors)

class Bus(Object):

    """list of listeners"""

    objs = []

    @staticmethod
    def add(obj) -> None:
        """add a listener"""
        Bus.objs.append(obj)

    @staticmethod
    def announce(txt) -> None:
        """echo text to listeners"""
        for obj in Bus.objs:
            obj.announce(txt)

    @staticmethod
    def byorig(orig) -> Object:
        """return listener by origin"""
        for obj in Bus.objs:
            if repr(obj) == orig:
                return obj
        return None

    @staticmethod
    def remove(obj) -> None:
        """remove a listener"""
        try:
            Bus.objs.remove(obj)
        except ValueError:
            pass

    @staticmethod
    def say(orig, txt, channel=None) -> None:
        """print text on a specific listeners channel"""
        listener = Bus.byorig(orig)
        if listener:
            if channel:
                listener.say(channel, txt)
            else:
                listener.raw(txt)

class Commands(Object):

    """commands binded to a function"""

    cmds = Object()
    modnames = Object()

    @staticmethod
    def add(func) -> None:
        """add a function"""
        cmd = func.__name__
        setattr(Commands.cmds, cmd, func)
        setattr(Commands.modnames, cmd, func.__module__)

    @staticmethod
    def handle(evt):
        # pylint: disable=W0718
        """handle an event"""
        parse(evt, evt.txt)
        func = getattr(Commands.cmds, evt.cmd, None)
        if not func:
            modname = getattr(Commands.modnames, evt.cmd, None)
            mod = None
            if modname:
                Logging.debug(f"load {modname}")
                pkg = sys.modules.get("opr.modules")
                mod = getattr(
                              pkg,
                              modname.split(".")[-1],
                              None
                             )
                func = getattr(mod, evt.cmd, None)
        if func:
            try:
                func(evt)
                evt.show()
            except Exception as ex:
                Errors.handle(ex)
        evt.ready()
        return evt

    @staticmethod
    def remove(func) -> None:
        """remove a function"""
        cmd = func.__name__.split(".")[-1]
        if cmd in keys(Commands.cmds):
            delattr(Commands.cmds, cmd)
        if cmd in keys(Commands.modnames):
            delattr(Commands.modnames, cmd)

    @staticmethod
    def unload(mod):
        """remove functions in a module"""
        for _key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if 'event' in cmd.__code__.co_varnames:
                Commands.remove(cmd)

    @staticmethod
    def scan(mod) -> None:
        """Scan and register functions found in a module"""
        for _key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if 'event' in cmd.__code__.co_varnames:
                Commands.add(cmd)

class Event(Default):

    """event occured"""

    __slots__ = ('_ready', '_thr')

    def __init__(self, *args, **kwargs):
        Default.__init__(self, *args, **kwargs)
        self._ready = threading.Event()
        self._thr = None
        self.result = []
        self.txt = ""

    def bot(self):
        """originating bot"""
        assert self.orig
        return Bus.byorig(self.orig)

    def parse(self):
        """parse this event"""
        parse(self, self.txt)

    def ready(self) -> None:
        """signal event as ready"""
        self._ready.set()

    def reply(self, txt) -> None:
        """add text to result list"""
        self.result.append(txt)

    def show(self) -> None:
        """display result list"""
        for txt in self.result:
            Bus.say(self.orig, txt, self.channel)

    def wait(self) -> []:
        """wait for event to finish and return result"""
        if self.thr:
            self.thr.join()
        self._ready.wait()
        return self.result

class Handler(Object):

    """handle event by calling typed callbacks"""

    def __init__(self):
        Object.__init__(self)
        self.cbs = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.register('event', Commands.handle)
        Bus.add(self)

    def announce(self, txt) -> None:
        """announce on channel"""
        self.raw(txt)

    def event(self, txt) -> Event:
        """create an event and set its origin to this handler"""
        msg = Event()
        msg.type = 'event'
        msg.orig = repr(self)
        msg.txt = txt
        return msg

    def handle(self, evt) -> Event:
        # pylint: disable=W0212
        """handle an event"""
        func = getattr(self.cbs, evt.type, None)
        if func:
            evt._thr = launch(dispatch, func, evt, name=evt.cmd)
        return evt

    def loop(self) -> None:
        """loop handling events"""
        while not self.stopped.is_set():
            try:
                self.handle(self.poll())
            except (ssl.SSLError, EOFError, KeyboardInterrupt) as ex:
                Errors.handle(ex)
                self.restart()

    def one(self, txt) -> Event:
        """handle one event"""
        return self.handle(self.event(txt))

    def poll(self) -> Event:
        """return event from queue"""
        return self.queue.get()

    def put(self, evt) -> None:
        """put event into the queue"""
        self.queue.put_nowait(evt)

    def raw(self, txt) -> None:
        """print on display"""

    def say(self, channel, txt) -> None:
        "print in specific channel"
        if channel:
            self.raw(txt)

    def register(self, typ, func) -> None:
        """register a callback with a type"""
        setattr(self.cbs, typ, func)

    def restart(self) -> None:
        """stop and start"""
        self.stop()
        self.start()

    def start(self) -> None:
        """start loop'n"""
        launch(self.loop)

    def stop(self) -> None:
        """stop loop'n"""
        self.stopped.set()
        self.queue.put_nowait(None)


# UTILITY


def command(cli, txt) -> Event:
    """run a command on a cli"""
    evt = cli.event(txt)
    Commands.handle(evt)
    evt.ready()
    return evt

def dispatch(func, evt) -> None:
    # pylint: disable=W0718
    """basic dispatcher"""
    try:
        func(evt)
    except Exception as ex:
        exc = ex.with_traceback(ex.__traceback__)
        Errors.errors.append(exc)
        evt.ready()

def parse(obj, txt):
    """parse text for commands"""
    obj.cmd = ""
    obj.args = []
    obj.gets = {}
    obj.mod = ""
    obj.opts = ""
    obj.otxt = txt
    obj.rest = ""
    obj.sets = {}
    for spli in txt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                obj.mod += f",{value}"
                continue
            obj.sets[key] = value
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            obj.gets[key] = value
            continue
        if not obj.cmd:
            obj.cmd = spli
            continue
        obj.args.append(spli)
    obj.txt = obj.cmd
    if obj.args:
        obj.rest = str(" ".join(obj.args))
        if obj.rest:
            obj.txt += " " + obj.rest

def scanstr(pkg, mods, init=None, doall=False, wait=False) -> None:
    """scan a package for list of modules"""
    res = []
    path = pkg.__path__[0]
    if doall:
        modlist = [x[:-3] for x in os.listdir(path) if x.endswith(".py") and x != "__init__.py"]
        mods = ",".join(sorted(modlist))
    threads = []
    for modname in spl(mods):
        module = getattr(pkg, modname, None)
        if module:
            if not init:
                Commands.scan(module)
        if init and "start" in dir(module):
            threads.append(launch(module.start))
        res.append(module)
    if wait:
        for thread in threads:
            thread.join()
    return res

def waiter(clear=True):
    """poll for errors"""
    got = []
    for ex in Errors.errors:
        stream = io.StringIO(
                             traceback.print_exception(
                                                       type(ex),
                                                       ex,
                                                       ex.__traceback__
                                                      )
                            )
        for line in stream.readlines():
            Logging.debug(line)
        got.append(ex)
    if clear:
        for exc in got:
            Errors.errors.remove(exc)
