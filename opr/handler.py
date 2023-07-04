# This file is placed in the Public Domain.


"handler"


# IMPORTS


import inspect
import queue
import ssl
import sys
import threading


from opr.loggers import Logging
from opr.objects import Default, Object, copy, keys
from opr.threads import launch
from opr.utility import spl


# DEFINES


def __dir__():
    return (
            'Bus',
            'Cfg',
            'Commands',
            'Errors',
            'Event',
            'Handler',
            "dispatch",
            "parse"
           )


MODNAMES = {
           }


Cfg = Default()


# CLASSES


class Errors(Object):

    "list of errors"

    errors = []

    @staticmethod
    def handle(ex) -> None:
        "store exception in the errors list"
        exc = ex.with_traceback(ex.__traceback__)
        Errors.errors.append(exc)


    @staticmethod
    def size():
        "return number of errors"
        return len(Errors.errors)


class Bus(Object):

    "list of listeners"

    objs = []

    @staticmethod
    def add(obj) -> None:
        "add a listener"
        Bus.objs.append(obj)

    @staticmethod
    def announce(txt) -> None:
        "echo text to listeners"
        for obj in Bus.objs:
            obj.announce(txt)

    @staticmethod
    def byorig(orig) -> Object:
        "return listener by origin"
        for obj in Bus.objs:
            if repr(obj) == orig:
                return obj
        return None

    @staticmethod
    def remove(obj) -> None:
        "remove a listener"
        try:
            Bus.objs.remove(obj)
        except ValueError:
            pass

    @staticmethod
    def say(orig, txt, channel=None) -> None:
        "print text on a specific listeners channel"
        listener = Bus.byorig(orig)
        if listener:
            if channel:
                listener.say(channel, txt)
            else:
                listener.raw(txt)


class Commands(Object):

    "commands binded to a function"

    cmds = Object()
    modnames = copy(Object(), MODNAMES)

    @staticmethod
    def add(func) -> None:
        "add a function"
        cmd = func.__name__
        setattr(Commands.cmds, cmd, func)
        setattr(Commands.modnames, cmd, func.__module__)

    @staticmethod
    def handle(evt):
        # pylint: disable=W0718
        "handle an event"
        evt.parse(evt.txt)
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
        "remove a function"
        cmd = func.__name__.split(".")[-1]
        if cmd in keys(Commands.cmds):
            delattr(Commands.cmds, cmd)
        if cmd in keys(Commands.modnames):
            delattr(Commands.modnames, cmd)

    @staticmethod
    def unload(mod):
        "remove functions in a module"
        for _key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if 'event' in cmd.__code__.co_varnames:
                Commands.remove(cmd)

    @staticmethod
    def scan(mod) -> None:
        "Scan and register functions found in a module"
        for _key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if 'event' in cmd.__code__.co_varnames:
                Commands.add(cmd)


class Event(Default):

    "event occured"

    __slots__ = ('_ready', '_thr')

    def __init__(self, *args, **kwargs):
        Default.__init__(self, *args, **kwargs)
        self._ready = threading.Event()
        self.result = []
        self.thr = None

    def bot(self):
        "originating bot"
        assert self.orig
        return Bus.byorig(self.orig)

    def parse(self, txt) -> None:
        "parse text for commands"
        parse(self, txt)

    def ready(self) -> None:
        "signal event as ready"
        self._ready.set()

    def reply(self, txt) -> None:
        "add text to result list"
        self.result.append(txt)

    def show(self) -> None:
        "display result list"
        for txt in self.result:
            Bus.say(self.orig, txt, self.channel)

    def wait(self) -> []:
        "wait for event to finish and return result"
        if self.thr:
            self.thr.join()
        self._ready.wait()
        return self.result


class Handler(Object):

    "handle event by calling typed callbacks"

    def __init__(self):
        Object.__init__(self)
        self.cbs = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.register('command', Commands.handle)
        Bus.add(self)

    def announce(self, txt) -> None:
        "announce on channel"
        self.raw(txt)

    def event(self, txt) -> Event:
        "create an event and set its origin to this handler"
        msg = Event()
        msg.type = 'command'
        msg.orig = repr(self)
        msg.parse(txt)
        return msg

    def handle(self, evt) -> Event:
        "handle an event"
        func = getattr(self.cbs, evt.type, None)
        if func:
            evt.thr = launch(dispatch, func, evt, name=evt.cmd)
        return evt

    def loop(self) -> None:
        "loop handling events"
        while not self.stopped.is_set():
            try:
                self.handle(self.poll())
            except (ssl.SSLError, EOFError, KeyboardInterrupt) as ex:
                Errors.handle(ex)
                self.restart()

    def one(self, txt) -> Event:
        "handle one event"
        return self.handle(self.event(txt))

    def poll(self) -> Event:
        "return event from queue"
        return self.queue.get()

    def put(self, evt) -> None:
        "put event into the queue"
        self.queue.put_nowait(evt)

    def raw(self, txt) -> None:
        "print on display"

    def say(self, channel, txt) -> None:
        "print in specific channel"
        if channel:
            self.raw(txt)

    def register(self, typ, func) -> None:
        "register a callback with a type"
        setattr(self.cbs, typ, func)

    def restart(self) -> None:
        "stop and start"
        self.stop()
        self.start()

    def start(self) -> None:
        "start loop'n"
        launch(self.loop)

    def stop(self) -> None:
        "stop loop'n"
        self.stopped.set()
        self.queue.put_nowait(None)


# UTILITY


def dispatch(func, evt) -> None:
    # pylint: disable=W0718
    "basic dispatcher"
    try:
        func(evt)
    except Exception as ex:
        exc = ex.with_traceback(ex.__traceback__)
        Errors.errors.append(exc)
        evt.ready()


# METHODS


def parsequal(obj, word):
    "check for qualness"
    try:
        key, value = word.split('==')
        if not obj.skip:
            obj.skip = Default()
        if value.endswith('-'):
            value = value[:-1]
            setattr(obj.skip, value, '')
        if not obj.gets:
            obj.gets = Default()
        setattr(obj.gets, key, value)
        return True
    except ValueError:
        return False


def parseassign(obj, word):
    "check for assign"
    try:
        key, value = word.split('=')
        if key == "mod":
            if not obj.mod:
                obj.mod = ""
            for val in spl(value):
                if val not in obj.mods:
                    obj.mods += f",{val}"
            return True
        if not obj.sets:
            obj.sets = Default()
        setattr(obj.sets, key, value)
        return True
    except ValueError:
        return False


def parseoption(obj, word):
    "check for options"
    if word.startswith('-'):
        if not obj.index:
            obj.index = 0
        try:
            obj.index = int(word[1:])
        except ValueError:
            if not obj.opts:
                obj.opts = ""
            obj.opts = obj.opts + word[1:]
        return True
    return False


def parse(obj, txt):
    "parse text for commands and arguments/options"
    obj.otxt = txt
    splitted = obj.otxt.split()
    args = []
    _nr = -1
    for word in splitted:
        if parseoption(obj, word):
            continue
        if parsequal(obj, word):
            continue
        if parseassign(obj, word):
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = word
            continue
        args.append(word)
    if args:
        obj.args = args
        obj.rest = ' '.join(args)
        obj.txt = obj.cmd + ' ' + obj.rest
    else:
        obj.txt = obj.cmd
