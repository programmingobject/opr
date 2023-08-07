# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0718


"threads"


import queue
import threading
import time
import types


from .errored import Errors


def __dir__():
    return (
            'Thread',
            'launch',
            'name'
           )


__all__ = __dir__()


class Thread(threading.Thread):

    ""

    def __init__(self, func, thrname, *args, daemon=True):
        super().__init__(None, self.run, thrname, (), {}, daemon=daemon)
        self._result = None
        self.name = thrname or name(func)
        self.queue = queue.Queue()
        self.queue.put_nowait((func, args))
        self.sleep = None
        self.starttime = time.time()

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def join(self, timeout=None):
        ""
        super().join(timeout)
        return self._result

    def run(self):
        ""
        func, args = self.queue.get()
        try:
            self._result = func(*args)
        except Exception as ex:
            exc = ex.with_traceback(ex.__traceback__)
            Errors.errors.append(exc)
            if args:
                try:
                    args[0].ready()
                except AttributeError:
                    pass


def launch(func, *args, **kwargs):
    thrname = kwargs.get('name', '')
    thread = Thread(func, thrname, *args)
    thread.start()
    return thread


def name(obj) -> str:
    typ = type(obj)
    if isinstance(typ, types.ModuleType):
        return obj.__name__
    if '__self__' in dir(obj):
        return f'{obj.__self__.__class__.__name__}.{obj.__name__}'
    if '__class__' in dir(obj) and '__name__' in dir(obj):
        return f'{obj.__class__.__name__}.{obj.__name__}'
    if '__class__' in dir(obj):
        return obj.__class__.__name__
    if '__name__' in dir(obj):
        return f'{obj.__class__.__name__}.{obj.__name__}'
    return None
