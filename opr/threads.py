# This file is placed in the Public Domain.


"""threads"""


__author__ = "Bart Thate <programmingobject@gmail.com>"


# IMPORTS


import functools
import queue
import threading
import time
import types


# INTERFACE


def __dir__():
    return (
            'Thread',
            'launch',
            'name',
            'threaded'
           )


__all__ = __dir__()


# CLASSES


class Thread(threading.Thread):

    """seperate line of execution"""

    def __init__(self, func, thrname, *args, daemon=True):
        super().__init__(None, self.run, thrname, (), {}, daemon=daemon)
        self._result = None
        self.name = thrname or name(func)
        self.queue = queue.Queue()
        self.queue.put_nowait((func, args))
        self.sleep = None
        self.starttime = time.time()

    def __iter__(self):
        """iterate over this threads attributes"""
        return self

    def __next__(self):
        """part of iterate"""
        for k in dir(self):
            yield k

    def join(self, timeout=None):
        """join this thread"""
        super().join(timeout)
        return self._result

    def run(self):
        """run workload"""
        func, args = self.queue.get()
        self._result = func(*args)


# UTILITY


def launch(func, *args, **kwargs) -> Thread:
    """start a function in a thread"""
    thrname = kwargs.get('name', '')
    thread = Thread(func, thrname, *args)
    thread.start()
    return thread


def name(obj) -> str:
    """return full qualified name of an object"""
    typ = type(obj)
    if isinstance(typ, types.ModuleType):
        return obj.__name__
    if '__self__' in dir(obj):
        clz = obj.__self__.__class__.__name__
        nme = obj.__name__
        return f'{clz}.{nme}'
    if '__class__' in dir(obj) and '__name__' in dir(obj):
        clz = obj.__class__.__name__
        nme = obj.__name__
        return f'{clz}.{nme}'
    if '__class__' in dir(obj):
        return obj.__class__.__name__
    if '__name__' in dir(obj):
        clz = obj.__class__.__name__
        nme = obj.__name__
        return f'{clz}.{nme}'
    return None


def threaded(func, *args, **kwargs) -> None:

    """threaded decorator"""

    @functools.wraps(func)
    def threadedfunc(*args, **kwargs):
        """run function in a thread"""
        thread = launch(func, *args, **kwargs)
        if args:
            args[0].thr = thread
        return thread

    threadedfunc.args = args
    threadedfunc.kwargs = kwargs

    return threadedfunc
